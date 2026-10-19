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


if __name__ == "__main__":
    unittest.main()
