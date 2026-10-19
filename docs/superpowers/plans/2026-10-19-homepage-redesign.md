# Homepage Redesign Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the text-heavy homepage of sc-capoeira.de with the approved white, photo-led design (hero collage → times strip → what is capoeira → videos → training → kids → events → team), in EN and DE, with a new header, footer and font that the inner pages inherit.

**Architecture:** Each homepage section is a custom HugoBlox block, a partial at `layouts/partials/blocks/sc_<name>.html` that `parse_block_v2` picks up from `block: sc_<name>` in the `sections:` front matter of `content/{en,de}/_index.md`. Copy and images stay in front matter. Training times and FAQs live once in `data/`, and the blocks and the JSON-LD in `layouts/partials/custom_head.html` all read from there. The header and footer are swapped through HugoBlox's `header.navbar.block` / `footer.block` params. All styling lives in `assets/scss/template.scss`.

**Tech Stack:** Hugo 0.160.1 extended; HugoBlox modules `blox-bootstrap/v5` (Bootstrap 4 markup and JS) and `blox-core`; SCSS; Python 3.13 stdlib (`unittest`, `html.parser`, `json`, `tomllib`) for build tests.

**Spec:** `docs/superpowers/specs/2026-10-19-homepage-redesign-design.md`

## Global Constraints

- Hugo **0.160.1 extended**; `hugo --minify` must succeed. The only allowed warnings are the theme's existing `.Site.Data` / `.Site.AllPages` deprecation and `sitemap.xml` render-hook warnings.
- Every content change goes into **both** `content/en/` and `content/de/`. German copy is real German (given below). Internal DE links start with `/de/`.
- White background. Accents: yellow `#F7E018` (primary buttons and highlights), black `#111`, blue `#1E88E5` (kickers only).
- Font: **Archivo**, self-hosted (woff2 in `static/fonts/`). No request to fonts.googleapis.com.
- Styles go only in `assets/scss/template.scss` (`custom.scss` does not load).
- Keep these anchors on the homepage: `#trainings`, `#probetraining`, `#kids` (EN) / `#kinder` (DE).
- Keep the `seo:` front matter and the JSON-LD schema shape. Only the times, addresses and FAQ text become data-driven.
- One source for training times: `data/trainings.toml`. One source for FAQ text: `data/faq.toml`.
- Videos load YouTube (`youtube-nocookie.com`) only after a click. Before that, show a local still.
- The site-wide banner (`announcement` / `cascade.announcement` in both `_index.md` files) keeps working.
- No Impressum / Datenschutz links in this project.
- Work on branch `design/homepage-redesign`; PR to `main`; never push to `main`.

## Review Focus

1. **Phone width (375px):** the hero collage stacks under the text, cards become one column, the nav collapses into the burger menu, and there is no horizontal scroll. Covered by the manual browser check in Task 10 plus `test_no_fixed_wide_widths` in Task 2.
2. **Inner pages:** event, songs, people, contact, post and documents pages still build in EN and DE and show the new header and footer. Covered by `test_inner_pages_use_new_chrome` in Task 9.
3. **Banner:** it still shows on the homepage and on inner pages in both languages after the header swap. Covered by `test_announcement_still_rendered` in Task 9.
4. **German page:** no English copy leaks into DE blocks, and internal links keep `/de/`. Covered by `test_de_home_has_no_en_copy` and `test_de_internal_links_prefixed` in Task 10.
5. **Editing a session** in `data/trainings.toml` shows up in the strip, the cards and the JSON-LD alike. Covered by `test_sessions_match_data` (Task 3) and `test_jsonld_opening_hours_match_data` (Task 3).

---

## File Structure

| Path | Responsibility |
| --- | --- |
| `scripts/test_site.py` | Builds the site into a temp dir once; `unittest` tests over the HTML/JSON-LD output |
| `static/fonts/archivo-*.woff2` | Self-hosted Archivo 400/600/800/900 (latin) |
| `data/fonts/sc.toml` | HugoBlox font pack pointing headings/body/nav at Archivo |
| `assets/scss/template.scss` | `@font-face`, colour tokens, buttons, all `sc-*` component styles |
| `data/trainings.toml` | Locations + sessions (single source of times) |
| `data/faq.toml` | FAQ Q&A per language, `group = "general" \| "kids"` |
| `i18n/en.yaml`, `i18n/de.yaml` | Day abbreviations, group labels, small UI strings |
| `layouts/partials/sc/sessions.html` | Returns sessions (optionally filtered by group) enriched with their location |
| `layouts/partials/sc/faq_text.html` | Replaces `%kids_times%`, `%adults_times%`, `%locations%` placeholders in FAQ answers |
| `layouts/partials/sc/img.html` | Resizes an `assets/media/` image to webp and returns `<img>` (with alt, loading, width/height) |
| `layouts/partials/blocks/sc_hero.html` | Hero (white split + 3-photo collage) |
| `layouts/partials/blocks/sc_times_strip.html` | Slim strip of session chips |
| `layouts/partials/blocks/sc_tiles.html` | "What is capoeira" 4 tiles |
| `layouts/partials/blocks/sc_videos.html` | 1 large + 2 small click-to-load videos |
| `layouts/partials/blocks/sc_trainings.html` | Location cards + "first month free" card |
| `layouts/partials/blocks/sc_kids.html` | Kids section + kids FAQ |
| `layouts/partials/blocks/sc_faq.html` | General FAQ (`<details>`) |
| `layouts/partials/blocks/sc_events.html` | Latest event cards |
| `layouts/partials/blocks/sc_team.html` | Trainer avatars |
| `layouts/partials/components/headers/sc_navbar.html` | New header (copy of theme `navbar.html`, restyled, CTA item) |
| `layouts/partials/components/footers/sc_footer.html` | New black footer |
| `config/_default/menus.en.yaml`, `menus.de.yaml` | Per-language menus (replace `menus.yaml`) |
| `assets/media/home/*.jpg`, `assets/media/video/*.jpg` | Photos and video stills |
| `content/{en,de}/_index.md` | Section list and copy |

All `sc_*` blocks receive `.wcPage` and `.wcBlock` (HugoBlox convention). They read copy from `.wcBlock.content` and render inside the `<section id="…">` that `parse_block_v2` wraps around them. The section id comes from the block's `id:`.

---

### Task 1: Build test harness

**Files:**
- Create: `scripts/test_site.py`

**Interfaces:**
- Produces, importable by every later test in the same file:
  - `REPO: pathlib.Path = Path(__file__).resolve().parents[1]`
  - `PUBLIC: pathlib.Path`, the build output dir (set in `setUpModule`)
  - `read(path: str) -> str`, which reads `PUBLIC / path`
  - `home(lang: str) -> str`: `"en"` → `index.html`, `"de"` → `de/index.html`
  - `by_class(html: str, cls: str) -> list[dict]`, giving every element whose class list contains the token `cls` as `{"tag", "attrs": dict, "text": str, "pos": int}` (`pos` is the element's start offset in the HTML), in document order
  - `by_id(html: str, id: str) -> dict | None`
  - `hrefs(html: str) -> list[str]`
  - `jsonld(html: str) -> list[dict]`, parsing every `<script type="application/ld+json">`
  - `data(name: str) -> dict`, which loads `REPO / "data" / f"{name}.toml"` with `tomllib`

- [ ] **Step 1: Write the harness and a baseline test**

`setUpModule` runs `hugo --minify --quiet -d <tempdir>` from the repo root and fails the module if the exit code is non-zero. Implement the helpers above using `html.parser.HTMLParser` with an element stack, so that `text` is the concatenated text inside the element.

```python
class Baseline(unittest.TestCase):
    def test_home_builds_both_languages(self):
        self.assertIn("<html", home("en"))
        self.assertIn("de-de", home("de"))

    def test_existing_jsonld_parses(self):
        types = [g.get("@type") for d in jsonld(home("en")) for g in d.get("@graph", [d])]
        self.assertIn("FAQPage", types)
```

- [ ] **Step 2: Run it**

Run: `python3 scripts/test_site.py -v`
Expected: 2 tests PASS. If `existing_jsonld_parses` fails because the JSON-LD is not one `@graph`, adapt the helper, not the template.

- [ ] **Step 3: Commit**

```bash
git add scripts/test_site.py
git commit -m "Add build test harness for the homepage redesign"
```

---

### Task 2: Design foundation (font, tokens, buttons, no dark mode)

**Files:**
- Create: `static/fonts/archivo-{400,600,800,900}.woff2`, `data/fonts/sc.toml`
- Modify: `assets/scss/template.scss` (prepend the foundation; keep all existing rules)
- Modify: `config/_default/params.yaml` (`appearance.font: sc`, `header.navbar.show_day_night: false`)

**Interfaces:**
- Produces CSS custom properties on `:root`: `--sc-yellow: #F7E018; --sc-black: #111; --sc-blue: #1E88E5; --sc-grey-bg: #fafafa; --sc-radius: 18px;`
- Produces classes: `.sc-btn` (yellow pill), `.sc-btn--dark` (black pill, white text), `.sc-kicker` (11px, 800, uppercase, letter-spacing .18em, blue), `.sc-title` (bold section heading), `.sc-lead` (grey lead paragraph, max-width 560px), `.sc-mark` (yellow highlighter: `linear-gradient(transparent 58%, var(--sc-yellow) 58%)`), and `.sc-section--grey` (grey background).

- [ ] **Step 1: Write failing tests**

```python
class Foundation(unittest.TestCase):
    def css(self):
        return "".join(p.read_text() for p in PUBLIC.glob("**/*.css"))
    def test_archivo_self_hosted(self):
        self.assertIn("Archivo", self.css())
        self.assertTrue(list(PUBLIC.glob("fonts/archivo-*.woff2")))
        self.assertNotIn("fonts.googleapis.com", home("en"))
    def test_tokens_present(self):
        self.assertIn("--sc-yellow", self.css())
    def test_no_fixed_wide_widths(self):
        import re
        self.assertFalse(re.search(r"\.sc-[^{]*\{[^}]*(?<!max-)width:\s*(?:[5-9]\d\d|\d{4,})px", self.css()))
```

- [ ] **Step 2: Run, expect FAIL** (`python3 scripts/test_site.py Foundation -v`; Archivo is missing)

- [ ] **Step 3: Implement**
  - Download the latin woff2 files for weights 400/600/800/900 from `https://cdn.jsdelivr.net/npm/@fontsource/archivo@5/files/archivo-latin-<w>-normal.woff2` into `static/fonts/archivo-<w>.woff2`.
  - Add the `@font-face` rules (`font-display: swap`) and the tokens and classes above.
  - `data/fonts/sc.toml`: `name = "SC"`, `google_fonts = ""`, `heading_font = "Archivo"`, `body_font = "Archivo"`, `nav_font = "Archivo"`, `mono_font = ""`.
  - Set the params.

- [ ] **Step 4: Run, expect PASS.** Also run `hugo --minify` and check that only the allowed warnings appear.

- [ ] **Step 5: Commit** `git commit -m "Self-host Archivo, add SC design tokens, disable dark mode"`

---

### Task 3: Training data, times strip, data-driven JSON-LD times

**Files:**
- Create: `data/trainings.toml`, `i18n/en.yaml`, `i18n/de.yaml`, `layouts/partials/sc/sessions.html`, `layouts/partials/blocks/sc_times_strip.html`
- Modify: `layouts/partials/custom_head.html` (the `openingHoursSpecification` arrays and `hasCourseInstance` arrays, plus the `location` places, are generated from data)
- Modify: `content/{en,de}/_index.md` (insert `- block: sc_times_strip` right after the hero section)

**Interfaces:**
- `data/trainings.toml` shape (copy the values from today's `_index.md` and `custom_head.html`):

```toml
[[locations]]
key = "MELO"
name = "Marie-Elisabeth-Lüders-Oberschule"
room = { en = "upper gym", de = "Gymnastikhalle (oben)" }
street = "Steinmetzstr. 79"
postal_code = "10783"
district = "Schöneberg"
maps = "https://maps.app.goo.gl/BPBgbh3EvnWAD4Fo7"
geo = { lat = 52.499238779432005, lon = 13.36469710838366 }   # optional
# … KSG (Puttkamerstr. 19, 10969, Kreuzberg), TAM (Wilhelmstr. 116–117, 10963, Mitte)

[[sessions]]
group = "kids"            # "kids" | "adults"
location = "MELO"
days = ["Tuesday", "Thursday"]   # schema.org day names
opens = "17:00"
closes = "18:30"
# … Kids Fri 16:30–18:00 TAM; Adults Tue 18:00–19:30 KSG; Adults Fri 20:00–21:30 MELO
```

- `partial "sc/sessions.html" (dict "group" "kids")` returns a slice of maps `{group, days, opens, closes, location: <location map>}`. Without `group` it returns all sessions, ordered as in the file.
- i18n keys: `sc_day_short_<Day>` (EN Mon…Sun, DE Mo…So), `sc_group_kids` (Kids / Kinder), `sc_group_adults` (Adults / Erwachsene).
- The strip's root class is `sc-strip`. It renders one `.sc-strip__item` per **session**, in the form `<b>{day short(s) joined " & "}</b> {opens} {group label} · {location key}`. Example: `Tue & Thu 17:00 Kids · MELO`.

- [ ] **Step 1: Write failing tests**

```python
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
```

- [ ] **Step 2: Run, expect FAIL**

- [ ] **Step 3: Implement** the data file, i18n, `sc/sessions.html`, the strip block and its styles (`.sc-strip`: centered flex-wrap row, grey background, top and bottom border; the day pill is black with yellow text). Then rewrite the three hard-coded JSON-LD regions (`location[]` with its `openingHoursSpecification`, and both `hasCourseInstance` arrays) as `range` loops over the data. Emit JSON values with `| jsonify`. Keep every other key byte-for-byte.

- [ ] **Step 4: Run, expect PASS**

- [ ] **Step 5: Commit** `git commit -m "Move training times to data/trainings.toml; add times strip"`

---

### Task 4: Hero block and photos

**Files:**
- Create: `layouts/partials/sc/img.html`, `layouts/partials/blocks/sc_hero.html`
- Create: `assets/media/home/roda-kick.jpg` (from `https://i.ytimg.com/vi/dm_Bwea-thM/maxresdefault.jpg`), `home/au.jpg` (`94x_-eeQqY4`), `home/kids.jpg` (`5mgMGsqMNkw`), `home/kids-training.jpg` (`6Fk1dvp1te0`)
- Modify: `content/{en,de}/_index.md` (replace the `hero` section)

**Interfaces:**
- `partial "sc/img.html" (dict "src" "home/au.jpg" "alt" "…" "width" 900 "class" "…" "eager" false)` returns `<img>` resized to `<width>x webp`, with `width`/`height` attributes, `loading="lazy"` unless eager is set, and `class`. It calls `errorf` if the file is missing.
- Front matter for `sc_hero`:

```yaml
- block: sc_hero
  content:
    kicker: Capoeira in Berlin
    title: 'Dance, acrobatics, music, fight &'
    highlight: 'fun.'
    text: "That's capoeira. Kids and adults in Schöneberg, Kreuzberg and Mitte. Your first month is free."
    button: { text: Try a free training, url: '#trainings' }
    images:
      - { src: home/au.jpg, alt: '…', position: '60% center' }        # tall, left
      - { src: home/roda-kick.jpg, alt: '…', position: 'center' }
      - { src: home/kids.jpg, alt: '…', position: 'center' }
```

- DE copy: kicker `Capoeira in Berlin`; title `Tanz, Akrobatik, Musik, Kampf und`; highlight `Spaß!`; text `Das ist Capoeira. Für Kinder und Erwachsene in Schöneberg, Kreuzberg und Mitte. Dein erster Monat ist kostenlos.`; button `Kostenlos ausprobieren` → `#trainings`. Write descriptive alt texts in each language.
- Root element class `sc-hero`. Markup: `<h1 class="sc-hero__title">{title} <mark class="sc-mark">{highlight}</mark></h1>`. The first image is `eager`.
- Layout: a 2-column grid (text 1fr, collage 1.15fr). The collage is a grid with the first image spanning 2 rows, `border-radius: var(--sc-radius)` and `object-fit: cover`. Below 768px it collapses to one column with the collage under the text at 260px height.

- [ ] **Step 1: Write failing tests**

```python
class Hero(unittest.TestCase):
    def test_hero(self):
        for lang, word in (("en", "fun."), ("de", "Spaß!")):
            h = home(lang)
            self.assertEqual(len(by_class(h, "sc-hero")), 1)
            self.assertEqual(by_class(h, "sc-mark")[0]["text"].strip(), word)
            self.assertEqual(len(by_class(h, "sc-hero__img")), 3)
            self.assertTrue(all(i["attrs"].get("alt") for i in by_class(h, "sc-hero__img")))
            self.assertEqual(len([t for t in by_class(h, "sc-hero__title") if t["tag"] == "h1"]), 1)
```

- [ ] **Step 2: Run, expect FAIL**
- [ ] **Step 3: Implement** (download the stills with `curl -fsSL -o …`, write the block, styles and front matter).
- [ ] **Step 4: Run, expect PASS**. Open `hugo server` and look at `/` and `/de/` at desktop width and at 375px width.
- [ ] **Step 5: Commit** `git commit -m "Add photo-collage hero"`

---

### Task 5: "What is capoeira" tiles

**Files:**
- Create: `layouts/partials/blocks/sc_tiles.html`
- Modify: `content/{en,de}/_index.md` (insert after `sc_times_strip`, with `id: what-is-capoeira`)

**Interfaces:**
- Root element class `sc-tiles`. Front matter: `content.{kicker, title, lead, items: [{title, text, image: {src, alt, position}}]}`. Each item renders as `.sc-tile` containing `.sc-tile__img`, `h3`, and `p`.
- Images: Movement `home/au.jpg`; The roda `home/roda-kick.jpg`; Music `SC_example_horda.jpeg` (position `85% center`); Community `welcome.jpg` (position `center 60%`).
- EN copy: kicker `What is capoeira?`; title `An Afro-Brazilian art you play, not just train.`; lead `Two players meet in the roda, a circle of people singing and clapping, led by the berimbau.` Items:
  - Movement: `Ginga, kicks and escapes. Strength, flexibility and flow.`
  - The roda: `A game of question and answer between two players.`
  - Music: `Berimbau, pandeiro, atabaque and songs in Portuguese.`
  - Community: `An international group, all ages, all levels.`
- DE copy: kicker `Was ist Capoeira?`; title `Eine afro-brasilianische Kunst, die man spielt – nicht nur trainiert.`; lead `Zwei Spieler begegnen sich in der Roda, einem Kreis aus singenden und klatschenden Menschen, angeführt vom Berimbau.` Items:
  - Bewegung: `Ginga, Tritte und Ausweichbewegungen. Kraft, Beweglichkeit und Flow.`
  - Die Roda: `Ein Spiel aus Frage und Antwort zwischen zwei Spielern.`
  - Musik: `Berimbau, Pandeiro, Atabaque und Lieder auf Portugiesisch.`
  - Gemeinschaft: `Eine internationale Gruppe – alle Altersstufen, alle Levels.`
- Grid: 4 columns, 2 at ≤992px, 1 at ≤576px.

- [ ] **Step 1: Failing test:** `by_class(home(lang), "sc-tile")` has 4 entries per language, each containing an `img` with non-empty alt. The DE `h3` texts equal `["Bewegung","Die Roda","Musik","Gemeinschaft"]`.
- [ ] **Step 2: Run, expect FAIL**
- [ ] **Step 3: Implement**
- [ ] **Step 4: Run, expect PASS**
- [ ] **Step 5: Commit** `git commit -m "Add 'What is capoeira' tiles"`

---

### Task 6: Click-to-load videos

**Files:**
- Create: `layouts/partials/blocks/sc_videos.html`, `assets/media/video/{dm_Bwea-thM,94x_-eeQqY4,orfPSga_t-c}.jpg` (from `https://i.ytimg.com/vi/<id>/maxresdefault.jpg`)
- Modify: `content/{en,de}/_index.md` (insert after tiles: `id: videos`, `design.css_class: sc-section--grey`)

**Interfaces:**
- Root element class `sc-videos`. Front matter: `content.{kicker, title, lead, channel_url, channel_text, videos: [{id, title}]}`. The first video is large.
- Each video renders `<button class="sc-video" data-yt="<id>" aria-label="Play: <title>">`, containing the local still (via `sc/img.html`, src `video/<id>.jpg`) and a yellow round play icon. A small inline script (emitted once per page) replaces the button with `<iframe src="https://www.youtube-nocookie.com/embed/<id>?autoplay=1" allow="autoplay; encrypted-media; picture-in-picture" allowfullscreen title="<title>">` in a 16:9 wrapper.
- Videos: `dm_Bwea-thM` "Batizado e Troca de Cordas Berlin 2024" (large), `94x_-eeQqY4` "First day welcome Roda", `orfPSga_t-c` "Batizado e troca de cordas Berlin Germany 2025".
- Copy: EN kicker `Watch`, title `See it in action`, lead `From our Batizados and rodas – more on our YouTube channel.`, link `YouTube channel →`. DE kicker `Anschauen`, title `Capoeira in Aktion`, lead `Von unseren Batizados und Rodas – mehr auf unserem YouTube-Kanal.`, link `Zum YouTube-Kanal →`. `channel_url` is `https://www.youtube.com/@SimplesmenteCapoeiraBerlin`.

- [ ] **Step 1: Failing test:** 3 `.sc-video` per language, each with a `data-yt` attr; the home HTML contains no `<iframe` with `youtube` in the src; `youtube-nocookie.com` appears in the inline script.
- [ ] **Step 2: Run, expect FAIL**
- [ ] **Step 3: Implement**
- [ ] **Step 4: Run, expect PASS.** In `hugo server`, click a video and confirm it plays.
- [ ] **Step 5: Commit** `git commit -m "Add click-to-load video section"`

---

### Task 7: Training section (`#trainings`, `#probetraining`)

**Files:**
- Create: `layouts/partials/blocks/sc_trainings.html`
- Modify: `content/{en,de}/_index.md`: replace the old `contact` block (`id: trainings`) with `- block: sc_trainings` `id: trainings`, placed after videos.

**Interfaces:**
- Root element class `sc-trainings`. Uses `partial "sc/sessions.html"`. It renders one `.sc-loc` card per location in `data.trainings.locations`, showing:
  - `.sc-loc__name` (key)
  - an address line `{street} · {district} ↗` linking to `maps` (`target=_blank rel=noopener`)
  - one `.sc-loc__row` per session at that location: `{group label}` and `{days short} {opens}–{closes}`
- After the location cards comes a yellow card `<div class="sc-free" id="probetraining">` with `content.free.title` and the `content.free.items` list.
- Copy: EN kicker `Train with us`, title `Where & when`, lead `Just come by – no registration and no experience needed.`, free title `First month free`, items `Comfortable sports clothes (long pants recommended)`, `Clean indoor sports shoes`, `Water & a good mood`. DE kicker `Trainiere mit uns`, title `Wo & wann`, lead `Komm einfach vorbei – ohne Anmeldung und ohne Vorerfahrung.`, free title `Erster Monat kostenlos`, items `Bequeme Sportkleidung (lange Hose empfohlen)`, `Saubere Hallenschuhe`, `Wasser & gute Laune`.
- Grid: 3 location cards + the free card in 4 columns; 2 columns at ≤992px; 1 column at ≤576px.

- [ ] **Step 1: Failing test:** per language, `by_id(h,"trainings")` and `by_id(h,"probetraining")` exist; there are 3 `.sc-loc`; the number of `.sc-loc__row` equals the number of sessions; the KSG card's text contains `18:00–19:30`; the `#trainings` section's HTML contains no `wg-contact` class.
- [ ] **Step 2: Run, expect FAIL**
- [ ] **Step 3: Implement**
- [ ] **Step 4: Run, expect PASS**
- [ ] **Step 5: Commit** `git commit -m "Add data-driven training section"`

---

### Task 8: FAQ data, kids section, general FAQ, data-driven FAQ JSON-LD

**Files:**
- Create: `data/faq.toml`, `layouts/partials/sc/faq_text.html`, `layouts/partials/blocks/sc_kids.html`, `layouts/partials/blocks/sc_faq.html`
- Modify: `layouts/partials/custom_head.html` (the FAQPage `mainEntity` is built from `data/faq.toml` in the current language)
- Modify: `content/{en,de}/_index.md`: replace the old `kids` markdown block with `sc_kids` (`id: kids` in EN, `id: kinder` in DE, `css_class: sc-section--grey`), placed after trainings. Add `sc_faq` (`id: faq`) right before the footer-side sections (see Task 10 for the final order).

**Interfaces:**
- `data/faq.toml`:

```toml
[[en]]
group = "general"     # "general" | "kids"
q = "Where can I do Capoeira in Berlin?"
a = "Simplesmente Capoeira Berlin e.V. trains at three locations in Berlin: %locations%. ..."
# ...
[[de]]
# same entries in German
```

- Entries:
  - EN `general`: the 7 questions currently in the JSON-LD FAQPage, copied verbatim, with literal times and addresses replaced by placeholders.
  - EN `kids`: the 4 parent FAQs from `content/en/_index.md`, verbatim.
  - DE `kids`: the 4 parent FAQs from `content/de/_index.md`, verbatim.
  - DE `general`: German translations of the 7 general questions, written to match the existing DE tone ("Du").
- `partial "sc/faq_text.html" (dict "text" $a "lang" $lang)` returns the text with these placeholders replaced, built from `sc/sessions.html` and the locations:
  - `%kids_times%`, e.g. `Tuesday and Thursday 17:00–18:30 at MELO (Schöneberg) and Friday 16:30–18:00 at TAM (Mitte)`
  - `%adults_times%`
  - `%locations%`, e.g. `MELO (Marie-Elisabeth-Lüders-Oberschule, Steinmetzstr. 79, 10783 Berlin-Schöneberg), …`
  Use full day names via the i18n keys `sc_day_<Day>` and the joiners `sc_and` (and / und) and `sc_at` (at / im).
- `sc_kids` (root class `sc-kids`) front matter: `content.{kicker, title, items[], image: {src: home/kids-training.jpg, alt}, faq_title}`. It renders:
  - a photo on one side; on the other, the kicker, title, bullet list and the kids-group sessions (from `sc/sessions.html` with group `kids`) as small chips
  - below that, a `.sc-faq` list of the `group = "kids"` entries, each as `<details class="sc-faq__item"><summary>q</summary><p>a</p></details>`
- `sc_faq` (root class `sc-faq-section`) renders the `group = "general"` entries in the same markup, under `content.title` (EN `Questions & answers` / DE `Fragen & Antworten`).
- Kids copy:
  - EN: kicker `For kids, ~6 to 14`; title `Capoeira for kids`; items `Acrobatics and balance, step by step`, `Music, instruments and singing`, `Confidence, rhythm and playing fair`, `Taught in German & English`; faq_title `Questions from parents`.
  - DE: kicker `Für Kinder von ca. 6 bis 14`; title `Capoeira für Kinder`; items `Akrobatik und Balance – Schritt für Schritt`, `Musik, Instrumente und Gesang`, `Selbstvertrauen, Rhythmus und Fairness`, `Unterricht auf Deutsch & Englisch`; faq_title `Häufige Fragen von Eltern`.

- [ ] **Step 1: Failing tests**

```python
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
        self.assertIsNotNone(by_id(home("en"), "kids")); self.assertIsNotNone(by_id(home("de"), "kinder"))
```

(The `summary` gets class `sc-faq__q` and the answer `<p>` gets class `sc-faq__a`.)

- [ ] **Step 2: Run, expect FAIL**
- [ ] **Step 3: Implement**
- [ ] **Step 4: Run, expect PASS**
- [ ] **Step 5: Commit** `git commit -m "Data-driven FAQ; add kids and FAQ sections"`

---

### Task 9: Header, footer, per-language menus

**Files:**
- Create: `layouts/partials/components/headers/sc_navbar.html`, `layouts/partials/components/footers/sc_footer.html`, `config/_default/menus.en.yaml`, `config/_default/menus.de.yaml`
- Delete: `config/_default/menus.yaml`
- Modify: `config/_default/params.yaml`: `header.navbar.block: sc_navbar`, `footer.block: sc_footer`

**Interfaces:**
- `sc_navbar.html` starts as a copy of the theme's `components/headers/navbar.html` (blox-bootstrap v5), keeping its collapse, search and language-chooser behaviour, with these changes:
  - add the brand text `SIMPLESMENTE CAPOEIRA` next to the logo
  - add class `sc-navbar` on the `<nav>`
  - a menu entry with `params: { cta: true }` renders as `<a class="sc-btn sc-nav-cta">` instead of a nav-link
  - styles: white background, no shadow, a bottom border `#f0f0f0`, 600-weight links
- `menus.en.yaml` (`main:`): Training `/#trainings` (10), Kids `/#kids` (20), Events `event` (30), Songs `songs` (40), Team `people` (50), Contact `contact` (60), Free training `/#trainings` (70, `params: {cta: true}`).
- `menus.de.yaml`: Training `/#trainings`, Kinder `/#kinder`, Events `event`, Lieder `songs`, Team `people`, Kontakt `contact`, Probetraining `/#trainings` (cta). The URLs must resolve to `/de/…` in DE output, which the test checks.
- `sc_footer.html`: a black band with:
  - `<b>` holding the club name (`site.Title`) and `© {year}`
  - links Contact/Kontakt → `contact`, News → `post`, Documents/Dokumente → `documents`, all language-prefixed with `relLangURL`
  - YouTube and Instagram links (URLs as in the spec)
  - footer link labels come from the i18n keys `sc_footer_contact`, `sc_footer_news`, `sc_footer_documents`
  Keep the theme's `powered-by` line (it is outside the footer block) and style it grey on black.

- [ ] **Step 1: Failing tests**

```python
INNER = ["event/index.html", "songs/index.html", "people/index.html", "contact/index.html", "post/index.html", "documents/index.html"]
class Chrome(unittest.TestCase):
    def test_inner_pages_use_new_chrome(self):
        for p in INNER + ["de/" + p for p in INNER]:
            h = read(p)
            self.assertTrue(by_class(h, "sc-navbar"), p); self.assertTrue(by_class(h, "sc-footer"), p)
    def test_menus(self):
        self.assertIn("/de/#kinder", hrefs(home("de"))); self.assertIn("/#kids", hrefs(home("en")))
        self.assertEqual(len(by_class(home("de"), "sc-nav-cta")), 1)
    def test_footer_links_localised(self):
        f = by_class(home("de"), "sc-footer")[0]["text"]
        self.assertIn("Dokumente", f); self.assertNotIn("Impressum", f)
    def test_announcement_still_rendered(self):
        if "announcement:" not in (REPO / "content/en/_index.md").read_text(): self.skipTest("no banner set")
        for p in ["index.html", "de/index.html", "event/index.html", "de/songs/index.html"]:
            self.assertIsNotNone(by_id(read(p), "announcement"), p)
```

- [ ] **Step 2: Run, expect FAIL**
- [ ] **Step 3: Implement**
- [ ] **Step 4: Run, expect PASS.** In `hugo server` at 375px width, check that the burger opens the menu and that the CTA shows as a pill.
- [ ] **Step 5: Commit** `git commit -m "New header and footer with per-language menus"`

---

### Task 10: Events, team, final page assembly

**Files:**
- Create: `layouts/partials/blocks/sc_events.html`, `layouts/partials/blocks/sc_team.html`
- Modify: `content/{en,de}/_index.md` (final section list), `README.md` (developer notes)

**Interfaces:**
- `sc_events` (root class `sc-events`): `content.{kicker, title, count: 2}`. It takes the `count` newest pages from `where site.RegularPages "Type" "event"`, sorted by `.Date` descending, in the current language. Each one renders as `<a class="sc-event" href=…>` containing:
  - a black date badge: year in yellow, plus the short month from `.Date`
  - the title in `h3`
  - `location` from front matter in `p`
- `sc_team` (root class `sc-team`): `content.{kicker, title, user_groups: [Trainer, Supervision], link_text}`. Select author pages exactly as the theme's `blocks/people.html` does. For each one, render `.sc-person`, containing:
  - the round avatar with a yellow 3px ring (`avatar.*` resource, resized to 168px)
  - the name (`.Title`)
  - the `role` param
  After the people, render a link to `people` with `link_text`.
- Copy:
  - EN: events kicker `Coming up`, title `Events`; team kicker `Who teaches`, title `Our team`, link `Meet the team →`.
  - DE: `Demnächst`, `Events`; `Wer unterrichtet`, `Unser Team`, `Lerne das Team kennen →`.
- **Final section order** in both `_index.md` files:
  `sc_hero`, `sc_times_strip`, `sc_tiles`, `sc_videos`, `sc_trainings`, `sc_kids`, `sc_events`, `sc_team`, `sc_faq`, `markdown` (`id: about-capoeira`).
- Remove: the old `markdown` `probetraining` block, the old events `collection`, the News `collection` and the `cta` "Meet the trainer" block.
- The new `about-capoeira` markdown block holds the old long SEO text from the removed `probetraining` block, verbatim, minus the duplicated locations/times list and the "what to bring" list (both are now in `sc_trainings`). It is wrapped as `<details class="sc-more"><summary>More about capoeira in Berlin</summary> … </details>` (DE: `Mehr über Capoeira in Berlin`).
- Keep `seo:`, `summary:`, `announcement:` and `cascade:` front matter unchanged.
- README: under "developer notes", add one line each saying that training times live in `data/trainings.toml`, FAQs in `data/faq.toml`, and that tests run with `python3 scripts/test_site.py`.

- [ ] **Step 1: Failing tests**

```python
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
            self.assertFalse(by_class(home(lang), "wg-collection")); self.assertFalse(by_class(home(lang), "wg-hero"))
    def test_events_and_team(self):
        self.assertEqual(len(by_class(home("en"), "sc-event")), 2)
        self.assertGreaterEqual(len(by_class(home("de"), "sc-person")), 3)
    def test_de_home_has_no_en_copy(self):
        h = home("de")
        for s in ["Try a free training", "What is capoeira", "See it in action", "Where & when", "Capoeira for kids", "Our team", "Questions & answers", "More about capoeira"]:
            self.assertNotIn(s, h)
    def test_de_internal_links_prefixed(self):
        bad = [u for u in hrefs(home("de")) if u.startswith("/") and not u.startswith(("/de/", "/css/", "/js/", "/fonts/", "/media/", "/#"))]
        self.assertEqual(bad, [])
```

(Each block's outermost element carries its listed class; the `sc_faq` block's root is `sc-faq-section`, so it isn't confused with the `.sc-faq` list in `sc_kids`.)

- [ ] **Step 2: Run, expect FAIL**
- [ ] **Step 3: Implement** the two blocks, the final front matter and the README lines.
- [ ] **Step 4: Run the full suite and the production build**

Run: `python3 scripts/test_site.py -v && hugo --minify`
Expected: all tests PASS; the build shows only the allowed warnings.

- [ ] **Step 5: Manual check** with `hugo server` in Chrome: `/` and `/de/` at 1280px and 375px. Check that:
  - there is no horizontal scroll
  - the collage stacks under the text
  - the banner shows and can be dismissed
  - videos play on click
  - the anchors `#trainings`, `#probetraining`, `#kids`/`#kinder` scroll to the right place
  - the FAQ `<details>` sections open

- [ ] **Step 6: Commit and open PR**

```bash
git add -A && git commit -m "Assemble redesigned homepage (EN/DE)"
git push -u fork design/homepage-redesign
gh pr create --repo simplycapoeira-berlin/website --base main --head daniloaleixo:design/homepage-redesign --title "Homepage redesign" --body "<summary, screenshots, link to spec>"
```
