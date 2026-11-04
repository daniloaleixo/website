"""Build tests for the site.

Builds the site once into a temp dir, then checks the generated HTML and JSON-LD.
Run: python3 scripts/test_site.py -v
"""

import json
import re
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
    r = subprocess.run(["hugo", "--minify", "-d", str(PUBLIC)], cwd=REPO, capture_output=True, text=True)
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


class TrainingSection(unittest.TestCase):
    def test_training_cards(self):
        n = len(data("trainings")["sessions"])
        for lang in ("en", "de"):
            h = home(lang)
            self.assertIsNotNone(by_id(h, "trainings"))
            self.assertIsNotNone(by_id(h, "probetraining"))
            locs = by_class(h, "sc-loc")
            self.assertEqual(len(locs), 3)
            self.assertEqual(len(by_class(h, "sc-loc__row")), n)
            ksg = next(l for l in locs if "KSG" in l["text"])
            self.assertIn("18:00–19:30", ksg["text"])
            self.assertNotIn("wg-contact", by_id(h, "trainings")["attrs"].get("class", ""))


class Faq(unittest.TestCase):
    def test_faq_jsonld_matches_page(self):
        for lang in ("en", "de"):
            h = home(lang)
            g = [x for d in jsonld(h) for x in d.get("@graph", [d])]
            faq = next(x for x in g if x.get("@type") == "FAQPage")
            page_qs = [i["text"].strip() for i in by_class(h, "sc-faq__q")]
            self.assertEqual(sorted(q["name"] for q in faq["mainEntity"]), sorted(page_qs))
            self.assertEqual(len(faq["mainEntity"]), len(data("faq")[lang]))

    def test_no_unreplaced_placeholders(self):
        for lang in ("en", "de"):
            self.assertNotIn("%", "".join(i["text"] for i in by_class(home(lang), "sc-faq__a")))

    def test_kids_anchor(self):
        self.assertIsNotNone(by_id(home("en"), "kids"))
        self.assertIsNotNone(by_id(home("de"), "kinder"))

    def test_kids_times_from_data(self):
        h = home("en")
        answer = next(a["text"] for q, a in zip(by_class(h, "sc-faq__q"), by_class(h, "sc-faq__a"))
                      if "kids in Berlin" in q["text"])
        self.assertIn("Tuesday and Thursday 17:00–18:30 at MELO (Schöneberg)", answer)


INNER = ["event/index.html", "songs/index.html", "people/index.html", "contact/index.html", "post/index.html", "documents/index.html"]


class Chrome(unittest.TestCase):
    def test_inner_pages_use_new_chrome(self):
        for p in INNER + ["de/" + p for p in INNER]:
            h = read(p)
            self.assertTrue(by_class(h, "sc-navbar"), p)
            self.assertTrue(by_class(h, "sc-footer"), p)

    def test_menus(self):
        self.assertIn("/de/#kinder", hrefs(home("de")))
        self.assertIn("/#kids", hrefs(home("en")))
        self.assertEqual(len(by_class(home("de"), "sc-nav-cta")), 1)

    def test_footer_links_localised(self):
        f = by_class(home("de"), "sc-footer")[0]["text"]
        self.assertIn("Dokumente", f)
        self.assertNotIn("Impressum", f)

    def test_announcement_still_rendered(self):
        # only when a banner is set; a commented-out one doesn't count
        if not re.search(r"^announcement:", (REPO / "content/en/_index.md").read_text(), re.M):
            self.skipTest("no banner set")
        for p in ["index.html", "de/index.html", "event/index.html", "de/songs/index.html"]:
            self.assertIsNotNone(by_id(read(p), "announcement"), p)


class Page(unittest.TestCase):
    ORDER = ["sc-hero", "sc-strip", "sc-tiles", "sc-videos", "sc-trainings", "sc-kids", "sc-events", "sc-team", "sc-faq-section", "sc-more"]

    def test_section_order(self):
        for lang in ("en", "de"):
            h = home(lang)
            found = {c: by_class(h, c) for c in self.ORDER}
            self.assertTrue(all(found.values()), [c for c, v in found.items() if not v])
            pos = [found[c][0]["pos"] for c in self.ORDER]
            self.assertEqual(pos, sorted(pos))

    def test_old_blocks_gone(self):
        for lang in ("en", "de"):
            self.assertFalse(by_class(home(lang), "wg-collection"))
            self.assertFalse(by_class(home(lang), "wg-hero"))

    def test_events_and_team(self):
        self.assertEqual(len(by_class(home("en"), "sc-event")), 2)
        self.assertGreaterEqual(len(by_class(home("de"), "sc-person")), 3)

    def test_de_home_has_no_en_copy(self):
        import re
        h = re.sub(r"<script.*?</script>", "", home("de"), flags=re.S)  # JSON-LD keywords are bilingual on purpose
        for s in ["Try a free training", "What is capoeira", "See it in action", "Where & when", "Capoeira for kids", "Our team", "Questions & answers", "More about capoeira"]:
            self.assertNotIn(s, h)

    def test_de_internal_links_prefixed(self):
        links = [e["attrs"]["href"] for e in _elements(home("de")) if "href" in e["attrs"] and "hreflang" not in e["attrs"]]  # skip the EN switch
        bad = [u for u in links if u.startswith("/") and not u.startswith(("/de/", "/css/", "/js/", "/fonts/", "/media/", "/#"))]
        self.assertEqual(bad, [])


class ReviewFixes(unittest.TestCase):
    def test_events_kicker_does_not_promise_future(self):
        # the block shows the newest events, which may be over already
        for lang, word in (("en", "Coming up"), ("de", "Demnächst")):
            kicker = [k["text"] for k in by_class(home(lang), "sc-kicker")
                      if k["pos"] > by_class(home(lang), "sc-events")[0]["pos"]][0]
            self.assertNotEqual(kicker.strip(), word)

    def test_de_video_labels_german(self):
        labels = [v["attrs"]["aria-label"] for v in by_class(home("de"), "sc-video")]
        self.assertTrue(all(l.startswith("Abspielen") for l in labels), labels)

    def test_h1_keeps_capoeira_berlin_keyword(self):
        for lang in ("en", "de"):
            h1 = [e for e in _elements(home(lang)) if e["tag"] == "h1" and "sc-hero__title" in e["attrs"].get("class", "")][0]
            self.assertIn("Capoeira in Berlin", h1["text"])

    def test_faq_ids_differ_per_language(self):
        ids = []
        for lang in ("en", "de"):
            g = [x for d in jsonld(home(lang)) for x in d.get("@graph", [d])]
            ids.append(next(x for x in g if x.get("@type") == "FAQPage")["@id"])
        self.assertNotEqual(ids[0], ids[1])


INNER = ["contact/index.html", "people/index.html", "event/index.html", "post/index.html",
         "songs/index.html", "documents/index.html", "documents/satzung/index.html", "event/batizado2026/index.html",
         "capoeira/index.html", "capoeira/what-is-capoeira/index.html", "capoeira/history-of-capoeira/index.html",
         "capoeira/zumbi-dos-palmares/index.html", "capoeira/besouro-manganga/index.html",
         "capoeira/berimbau-and-instruments/index.html", "capoeira/capoeira-angola-regional-contemporanea/index.html",
         "capoeira/mestre-bimba/index.html", "capoeira/mestre-pastinha/index.html",
         "capoeira/maculele/index.html", "capoeira/samba-de-roda/index.html",
         "capoeira/capoeira-unesco-heritage/index.html", "capoeira/candomble-and-capoeira/index.html",
         "capoeira/syncretism-orixas-and-saints/index.html"]


def meta(html, attr, value):
    return [e["attrs"].get("content", "") for e in _elements(html)
            if e["tag"] == "meta" and e["attrs"].get(attr) == value]


class Seo(unittest.TestCase):
    def pages(self):
        for path in ["index.html"] + INNER:
            for lang in ("en", "de"):
                yield f"{lang}: {path}", read(path if lang == "en" else f"de/{path}")

    def test_one_h1_per_page(self):
        for name, html in self.pages():
            with self.subTest(name):
                self.assertEqual(len([e for e in _elements(html) if e["tag"] == "h1"]), 1)

    def test_descriptions_are_own_and_plain(self):
        site_desc = meta(read("tags/index.html"), "name", "description")[0]
        for name, html in self.pages():
            with self.subTest(name):
                desc = meta(html, "name", "description")[0]
                self.assertTrue(desc)
                self.assertNotEqual(desc, site_desc)
                self.assertNotIn("**", desc)

    def test_hreflang_pairs_and_x_default(self):
        alts = {e["attrs"]["hreflang"]: e["attrs"]["href"] for e in _elements(read("de/contact/index.html"))
                if e["tag"] == "link" and "hreflang" in e["attrs"]}
        self.assertEqual(alts, {"en": "https://sc-capoeira.de/contact/", "de": "https://sc-capoeira.de/de/contact/",
                                "x-default": "https://sc-capoeira.de/contact/"})

    def test_og_locale(self):
        self.assertEqual(meta(home("en"), "property", "og:locale"), ["en_US"])
        self.assertEqual(meta(home("de"), "property", "og:locale"), ["de_DE"])
        self.assertEqual(meta(home("en"), "property", "og:updated_time"), [])

    def test_sitemap_has_only_real_pages(self):
        for lang in ("en", "de"):
            locs = read(f"{lang}/sitemap.xml")
            for junk in ("/admin/", "/tags/", "/categories/", "/authors/", "/publication-type/", "/publication_types/"):
                self.assertNotIn(junk, locs)
            self.assertIn("/contact/", locs)

    def test_listing_pages_noindex(self):
        for path in ("tags/index.html", "authors/index.html", "publication-type/paper-conference/index.html"):
            self.assertEqual(meta(read(path), "name", "robots"), ["noindex"], path)


ARTICLE = "capoeira/what-is-capoeira/index.html"
# article slug -> licence (or source) link its image caption must credit
IMAGE_CREDITS = {
    "what-is-capoeira": "https://creativecommons.org/licenses/by/2.0/",
    "history-of-capoeira": "https://commons.wikimedia.org/wiki/File:Rugendasroda.jpg",
    "zumbi-dos-palmares": "https://creativecommons.org/licenses/by-sa/4.0/",
    "besouro-manganga": "https://creativecommons.org/licenses/by-sa/2.0/",
    "berimbau-and-instruments": "https://creativecommons.org/licenses/by-sa/2.0/",
    "capoeira-angola-regional-contemporanea": "https://creativecommons.org/licenses/by/2.0/",
    "mestre-bimba": "https://creativecommons.org/licenses/by-sa/4.0/",
    "mestre-pastinha": "https://creativecommons.org/licenses/by-sa/4.0/",
    "maculele": "https://creativecommons.org/licenses/by/2.0/",
    "samba-de-roda": "https://creativecommons.org/licenses/by/4.0/",
    "capoeira-unesco-heritage": "https://creativecommons.org/licenses/by/2.0/",
    "candomble-and-capoeira": "https://creativecommons.org/licenses/by/3.0/br/deed.en",
    "syncretism-orixas-and-saints": "https://creativecommons.org/licenses/by/2.0/",
}
ARTICLES = [f"capoeira/{slug}/index.html" for slug in IMAGE_CREDITS]
# (from, to): article slugs that must link to each other, in the same language
CROSS_LINKS = [
    ("what-is-capoeira", "history-of-capoeira"),
    ("what-is-capoeira", "berimbau-and-instruments"),
    ("what-is-capoeira", "capoeira-angola-regional-contemporanea"),
    ("history-of-capoeira", "what-is-capoeira"),
    ("history-of-capoeira", "zumbi-dos-palmares"),
    ("history-of-capoeira", "besouro-manganga"),
    ("history-of-capoeira", "mestre-bimba"),
    ("history-of-capoeira", "mestre-pastinha"),
    ("zumbi-dos-palmares", "history-of-capoeira"),
    ("besouro-manganga", "history-of-capoeira"),
    ("berimbau-and-instruments", "capoeira-angola-regional-contemporanea"),
    ("capoeira-angola-regional-contemporanea", "mestre-bimba"),
    ("capoeira-angola-regional-contemporanea", "berimbau-and-instruments"),
    ("mestre-bimba", "mestre-pastinha"),
    ("mestre-pastinha", "mestre-bimba"),
    ("berimbau-and-instruments", "candomble-and-capoeira"),
    ("maculele", "samba-de-roda"),
    ("samba-de-roda", "maculele"),
    ("samba-de-roda", "capoeira-unesco-heritage"),
    ("capoeira-unesco-heritage", "samba-de-roda"),
    ("capoeira-unesco-heritage", "history-of-capoeira"),
    ("candomble-and-capoeira", "besouro-manganga"),
    ("candomble-and-capoeira", "syncretism-orixas-and-saints"),
    ("syncretism-orixas-and-saints", "candomble-and-capoeira"),
    ("what-is-capoeira", "capoeira-unesco-heritage"),
    ("history-of-capoeira", "capoeira-unesco-heritage"),
]


def lang_path(lang, path):
    return path if lang == "en" else f"{lang}/{path}"


class LearnCapoeira(unittest.TestCase):
    def test_seo_title_and_description_fit_search_results(self):
        # Google cuts titles at about 60 characters and descriptions at about 160
        for lang in ("en", "de"):
            for page in ARTICLES + ["capoeira/index.html"]:
                with self.subTest(lang=lang, page=page):
                    h = read(lang_path(lang, page))
                    title = [e["text"] for e in _elements(h) if e["tag"] == "title"][0]
                    desc = meta(h, "name", "description")[0]
                    self.assertLessEqual(len(title), 60, title)
                    self.assertLessEqual(len(desc), 160, desc)

    def test_social_sharing_tags(self):
        # WhatsApp, Facebook, LinkedIn and X read these for the link preview
        other = {"en": "de_DE", "de": "en_US"}
        for lang in ("en", "de"):
            for page in ARTICLES:
                with self.subTest(lang=lang, page=page):
                    h = read(lang_path(lang, page))
                    image = meta(h, "property", "og:image")[0]
                    self.assertTrue(image.startswith("https://sc-capoeira.de/") and image.endswith(".jpg"), image)
                    self.assertEqual(meta(h, "property", "og:image:width"), ["1200"])
                    self.assertEqual(meta(h, "property", "og:image:height"), ["630"])
                    self.assertTrue(meta(h, "property", "og:image:alt")[0])
                    # WhatsApp drops preview images that are too large
                    self.assertLess((PUBLIC / image.removeprefix("https://sc-capoeira.de/")).stat().st_size, 300_000)
                    self.assertEqual(meta(h, "name", "twitter:card"), ["summary_large_image"])
                    self.assertEqual(meta(h, "name", "twitter:image"), [image])
                    self.assertEqual(meta(h, "name", "twitter:title"), meta(h, "property", "og:title"))
                    self.assertEqual(meta(h, "property", "og:locale:alternate"), [other[lang]])
                    self.assertTrue(meta(h, "property", "article:published_time"))

    def test_articles_link_capoeirawiki(self):
        for lang in ("en", "de"):
            for page in ARTICLES:
                with self.subTest(lang=lang, page=page):
                    wiki = [u for u in hrefs(read(lang_path(lang, page))) if u.startswith("https://capoeirawiki.org/wiki/")]
                    self.assertGreaterEqual(len(wiki), 2, wiki)

    def test_hub_lists_article(self):
        for lang in ("en", "de"):
            with self.subTest(lang):
                prefix = "" if lang == "en" else "/de"
                links = hrefs(read(lang_path(lang, "capoeira/index.html")))
                for a in ARTICLES:
                    self.assertIn(f"{prefix}/{a.removesuffix('index.html')}", links)

    def test_article_has_train_with_us_box(self):
        sessions = data("trainings")["sessions"]
        for lang, a in [(l, a) for l in ("en", "de") for a in ARTICLES]:
            with self.subTest(lang=lang, article=a):
                html = read(lang_path(lang, a))
                box = by_class(html, "sc-join")
                self.assertEqual(len(box), 1)
                self.assertEqual(len(by_class(html, "sc-join__row")), len(sessions))
                home_url = "/#trainings" if lang == "en" else "/de/#trainings"
                self.assertEqual([b["attrs"]["href"] for b in by_class(html, "sc-join__btn")], [home_url])

    def test_article_jsonld(self):
        for lang, a in [(l, a) for l in ("en", "de") for a in ARTICLES]:
            with self.subTest(lang=lang, article=a):
                html = read(lang_path(lang, a))
                arts = [j for j in jsonld(html) if j.get("@type") == "Article"]
                self.assertEqual(len(arts), 1)
                self.assertEqual(arts[0]["author"]["@type"], "Organization")
                self.assertTrue(arts[0]["image"])
                self.assertEqual(meta(html, "property", "og:type"), ["article"])

    def test_featured_image_has_alt_and_credit(self):
        for lang, (slug, credit) in [(l, c) for l in ("en", "de") for c in IMAGE_CREDITS.items()]:
            with self.subTest(lang=lang, article=slug):
                html = read(lang_path(lang, f"capoeira/{slug}/index.html"))
                img = by_class(html, "featured-image")
                self.assertEqual(len(img), 1)
                self.assertTrue(img[0]["attrs"].get("alt"))
                self.assertIn(credit, hrefs(html))

    def test_article_hreflang(self):
        alts = {e["attrs"]["hreflang"]: e["attrs"]["href"] for e in _elements(read(ARTICLE))
                if e["tag"] == "link" and "hreflang" in e["attrs"]}
        self.assertEqual(alts["de"], "https://sc-capoeira.de/de/capoeira/what-is-capoeira/")
        self.assertEqual(alts["en"], "https://sc-capoeira.de/capoeira/what-is-capoeira/")

    def test_article_in_sitemap(self):
        for lang in ("en", "de"):
            for a in ARTICLES:
                self.assertIn("/" + a.removesuffix("index.html"), read(f"{lang}/sitemap.xml"))

    def test_articles_link_each_other_in_same_language(self):
        for lang, (src, dst) in [(l, c) for l in ("en", "de") for c in CROSS_LINKS]:
            with self.subTest(lang=lang, src=src, dst=dst):
                prefix = "" if lang == "en" else "/de"
                self.assertIn(f"{prefix}/capoeira/{dst}/", hrefs(read(lang_path(lang, f"capoeira/{src}/index.html"))))

    def test_articles_link_group_anthem(self):
        for lang in ("en", "de"):
            prefix = "" if lang == "en" else "/de"
            for slug in ("berimbau-and-instruments", "capoeira-angola-regional-contemporanea", "mestre-bimba"):
                with self.subTest(lang=lang, article=slug):
                    html = read(lang_path(lang, f"capoeira/{slug}/index.html"))
                    self.assertIn(f"{prefix}/songs/himno-simplesmente-capoeira/", hrefs(html))

    def test_links_into_section(self):
        for lang in ("en", "de"):
            with self.subTest(lang):
                prefix = "" if lang == "en" else "/de"
                links = hrefs(home(lang))
                self.assertIn(f"{prefix}/capoeira/", links)
                self.assertIn(f"{prefix}/capoeira/what-is-capoeira/", links)


if __name__ == "__main__":
    unittest.main()
