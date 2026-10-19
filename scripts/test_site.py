"""Build tests for the site.

Builds the site once into a temp dir, then checks the generated HTML and JSON-LD.
Run: python3 scripts/test_site.py -v
"""

import json
import shutil
import subprocess
import tempfile
import tomllib
import unittest
from html.parser import HTMLParser
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
PUBLIC = None
VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "source", "track", "wbr"}


def setUpModule():
    global PUBLIC
    PUBLIC = Path(tempfile.mkdtemp(prefix="sc-site-"))
    r = subprocess.run(["hugo", "--minify", "--quiet", "-d", str(PUBLIC)], cwd=REPO, capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError("hugo build failed:\n" + r.stdout + r.stderr)


def tearDownModule():
    if PUBLIC:
        shutil.rmtree(PUBLIC, ignore_errors=True)


def read(path):
    return (PUBLIC / path).read_text(encoding="utf-8")


def home(lang):
    return read("index.html" if lang == "en" else f"{lang}/index.html")


class _Elements(HTMLParser):
    """Collects every element as {tag, attrs, text, pos}, in document order."""

    def __init__(self, html):
        super().__init__(convert_charrefs=True)
        self.line_starts = [0]
        for i, c in enumerate(html):
            if c == "\n":
                self.line_starts.append(i + 1)
        self.elements, self.stack = [], []
        self.feed(html)
        self.close()

    def handle_starttag(self, tag, attrs):
        line, col = self.getpos()
        el = {"tag": tag, "attrs": {k: v or "" for k, v in attrs}, "text": "", "pos": self.line_starts[line - 1] + col}
        self.elements.append(el)
        if tag not in VOID:
            self.stack.append(el)

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in VOID:
            self.stack.pop()

    def handle_endtag(self, tag):
        for i in range(len(self.stack) - 1, -1, -1):
            if self.stack[i]["tag"] == tag:
                del self.stack[i:]
                return

    def handle_data(self, data):
        for el in self.stack:
            el["text"] += data


def _elements(html):
    return _Elements(html).elements


def by_class(html, cls):
    return [e for e in _elements(html) if cls in e["attrs"].get("class", "").split()]


def by_id(html, id):
    return next((e for e in _elements(html) if e["attrs"].get("id") == id), None)


def hrefs(html):
    return [e["attrs"]["href"] for e in _elements(html) if "href" in e["attrs"]]


def jsonld(html):
    return [json.loads(e["text"]) for e in _elements(html)
            if e["tag"] == "script" and e["attrs"].get("type") == "application/ld+json"]


def data(name):
    with open(REPO / "data" / f"{name}.toml", "rb") as f:
        return tomllib.load(f)


class Baseline(unittest.TestCase):
    def test_home_builds_both_languages(self):
        self.assertIn("<html", home("en"))
        self.assertIn("de-de", home("de"))

    def test_existing_jsonld_parses(self):
        types = [g.get("@type") for d in jsonld(home("en")) for g in d.get("@graph", [d])]
        self.assertIn("FAQPage", types)


class Foundation(unittest.TestCase):
    def css(self):
        return "".join(p.read_text() for p in PUBLIC.glob("**/*.css"))

    def test_archivo_self_hosted(self):
        self.assertIn("archivo", self.css().lower())  # the minifier lowercases font names
        self.assertTrue(list(PUBLIC.glob("fonts/archivo-*.woff2")))
        self.assertNotIn("fonts.googleapis.com", home("en"))

    def test_tokens_present(self):
        self.assertIn("--sc-yellow", self.css())

    def test_no_fixed_wide_widths(self):
        import re
        self.assertFalse(re.search(r"\.sc-[^{]*\{[^}]*(?<!max-)width:\s*(?:[5-9]\d\d|\d{4,})px", self.css()))


class Trainings(unittest.TestCase):
    def test_sessions_match_data(self):
        n = len(data("trainings")["sessions"])
        for lang in ("en", "de"):
            self.assertEqual(len(by_class(home(lang), "sc-strip__item")), n)

    def test_strip_localised(self):
        self.assertTrue(any("Di" in i["text"] and "Kinder" in i["text"] for i in by_class(home("de"), "sc-strip__item")))

    def test_jsonld_opening_hours_match_data(self):
        d = data("trainings")
        expected = sorted((day, s["opens"], s["closes"]) for s in d["sessions"] for day in s["days"])
        g = [x for doc in jsonld(home("en")) for x in doc.get("@graph", [doc])]
        org = next(x for x in g if "SportsClub" in x.get("@type", []))
        got = sorted((o["dayOfWeek"], o["opens"], o["closes"]) for p in org["location"] for o in p["openingHoursSpecification"])
        self.assertEqual(got, expected)


class Hero(unittest.TestCase):
    def test_hero(self):
        for lang, word in (("en", "fun."), ("de", "Spaß!")):
            h = home(lang)
            self.assertEqual(len(by_class(h, "sc-hero")), 1)
            self.assertEqual(by_class(h, "sc-mark")[0]["text"].strip(), word)
            self.assertEqual(len(by_class(h, "sc-hero__img")), 3)
            self.assertTrue(all(i["attrs"].get("alt") for i in by_class(h, "sc-hero__img")))
            self.assertEqual(len([t for t in by_class(h, "sc-hero__title") if t["tag"] == "h1"]), 1)


class Tiles(unittest.TestCase):
    def test_four_tiles_with_alt(self):
        for lang in ("en", "de"):
            h = home(lang)
            tiles = by_class(h, "sc-tile")
            self.assertEqual(len(tiles), 4)
            imgs = [e for e in by_class(h, "sc-tile__img") if e["tag"] == "img"]
            self.assertEqual(len(imgs), 4)
            self.assertTrue(all(i["attrs"].get("alt") for i in imgs))

    def test_de_tile_titles(self):
        h = home("de")
        start = by_class(h, "sc-tiles")[0]["pos"]
        titles = [e["text"].strip() for e in _elements(h) if e["tag"] == "h3" and e["pos"] > start][:4]
        self.assertEqual(titles, ["Bewegung", "Die Roda", "Musik", "Gemeinschaft"])


class Videos(unittest.TestCase):
    def test_click_to_load(self):
        for lang in ("en", "de"):
            h = home(lang)
            vids = by_class(h, "sc-video")
            self.assertEqual(len(vids), 3)
            self.assertTrue(all(v["attrs"].get("data-yt") for v in vids))
            self.assertFalse([e for e in _elements(h) if e["tag"] == "iframe" and "youtube" in e["attrs"].get("src", "")])
            scripts = "".join(e["text"] for e in _elements(h) if e["tag"] == "script")
            self.assertIn("youtube-nocookie.com", scripts)


if __name__ == "__main__":
    unittest.main()
