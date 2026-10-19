# Homepage redesign: design

Date: 2026-10-19
Status: approved

## Why

sc-capoeira.de looks like a 2000s info page. The top of the homepage shows the club logo above a
long paragraph, and below it come several walls of SEO text. Nothing on the first screen shows
what capoeira looks like, and nothing makes a visitor want to try it.

The goal is a lively, modern club site. Someone in Berlin who has never done capoeira should, in
a few seconds:

1. get what capoeira is (dance, acrobatics, music, fight and fun),
2. feel like trying it,
3. see where and when they can come, and that the first month is free.

The inspiration is the opening of https://www.capoeira-berlin.de/: a photo of a real roda with
"Tanz, Akrobatik, Musik, Kampf und Spaß! Das ist Capoeira". After that comes imagery of what
capoeira is, using **our own** photos and videos.

## Scope

- **This project: the homepage only** (`content/en/_index.md`, `content/de/_index.md`), plus the
  shared header and footer and the global look (fonts, colours, buttons). Every other page
  inherits the global look.
- **Later, as separate projects:** redesigning the other pages (events, songs, people, contact,
  documents, posts). This project must not break them. They should keep working and simply pick
  up the new fonts, colours and header and footer.

## Goals

- White stays the main colour. The accents come from the club logo: yellow (`~#F7E018`), black,
  and a little blue (`~#1E88E5`). Yellow is the main call-to-action colour.
- A modern bold sans-serif replaces the system font (my call: Archivo, or a similar grotesk; the
  builder may pick, as long as it is self-hosted or loaded without a cookie banner problem).
- Real photos of our group are the main visual element.
- Bilingual as today: EN at `/`, DE at `/de/`, with the same structure and properly written German
  (not machine-literal). The German hero line is "Tanz, Akrobatik, Musik, Kampf und Spaß!".
- It works well on phones. Most visitors will come from Instagram or Google on mobile (my guess).

## Non-goals

- No change of static-site generator or hosting. It stays Hugo + HugoBlox modules, deployed to
  GitHub Pages from `main`.
- No new content types, no CMS work, no new languages.
- No redesign of the inner pages in this project.

## Anti-goals (a failure even if it "works")

- Losing search ranking. The current homepage text is heavily SEO-tuned ("Capoeira Berlin",
  "Capoeira Kreuzberg", "Capoeira für Kinder Berlin" …), and the `seo.title`/`seo.description`,
  JSON-LD (`layouts/partials/custom_head.html`) and the `#trainings`, `#probetraining` and
  `#kids`/`#kinder` anchors are relied on. The keyword text may move lower on the page or into
  `<details>`/shorter copy, but it must not simply disappear (my call; see "Left to the builder").
- A dark, heavy page. The user explicitly chose the bright white version over a dark full-bleed
  photo carousel.
- Training times that differ between the hero strip, the training section and the kids section.
  There must be one source for the times.
- The site-wide announcement banner (`announcement` / `cascade.announcement`, see the
  `/site-banner` skill) stops showing or looks broken.

## The homepage, top to bottom

The user approved this order and the look of the mockup (a white hero with a photo collage).

1. **Header.** Logo plus "SIMPLESMENTE CAPOEIRA" on the left. On the right, a few clear links:
   Training, Kids, Events, Songs, Team, Contact, a small yellow "Free training" button, and the
   EN/DE switch. Clean and white, with no heavy bar. On mobile it collapses into a menu.
   Menu details (my calls):
   - "People" is renamed "Team"/"Team" everywhere, keeping the URL `/people/`.
   - News and Documents leave the header but stay reachable from the footer.
   - Training and Kids link to homepage anchors, which differ per language (`#kids` vs
     `#kinder`), so the menus become per-language (`languages.yaml` or `menus.<lang>.yaml`).
2. **Hero (white, split).**
   - Left: a small kicker ("Capoeira in Berlin"), a big bold headline ("Dance, acrobatics, music,
     fight & fun." / "Tanz, Akrobatik, Musik, Kampf und Spaß!") with a yellow highlighter on the
     last word, one sentence (that's capoeira; kids and adults in Schöneberg, Kreuzberg and
     Mitte; first month free), and a yellow pill button "Try a free training" that goes to the
     training section.
   - Right: a collage of 3 photos with rounded corners (one tall on the left, two stacked on the
     right): an acrobatic move, a game in the roda, the kids.
3. **Training-times strip.** A slim strip directly under the hero, e.g. "Tue 18:00 Adults · KSG",
   "Fri 20:00 Adults · MELO", "Kids Tue · Thu · Fri".
4. **What is capoeira.** A kicker, a headline ("An Afro-Brazilian art you play, not just train."),
   one lead sentence, and **4 photo tiles**: Movement, The roda, Music, Community. Each has a
   photo and one short line.
5. **Videos ("See it in action").** One large video plus two small ones from the club's YouTube
   channel, with a link to the channel. Videos should not load YouTube until clicked: a thumbnail
   with a yellow play button (privacy plus speed; my call).
6. **Training: where & when** (keeps anchor `#trainings`). One card per location (MELO, KSG, TAM)
   with its address (a Google Maps link, as today) and its sessions, plus a yellow "First month
   free" card with what to bring. The current "free trial month / what to bring" content
   (`#probetraining`) lives here or right after.
7. **Kids** (keeps anchor `#kids` / `#kinder`). A photo on one side; on the other, a kicker
   ("For kids, ~6 to 14"), 4 short bullet points and a button to the kids details and parent FAQ.
   The FAQ stays on the homepage under the section (collapsed is fine) until the inner pages get
   redesigned (my call).
8. **Events.** Compact cards for the latest 2 events from `content/*/event/`, as the homepage
   shows today.
9. **Team.** Round photos with a yellow ring for the trainers (from `content/*/authors/`), linking
   to the people page.
10. **Footer.** Black: club name; Contact, News and Documents links; YouTube and Instagram links.
    No Impressum / Datenschutz links for now: those pages don't exist yet and are a separate
    issue (the user's decision).

Removed from the homepage: the **News** block (it can come back later; the post pages remain)
and the bottom "Meet the trainer →" CTA, which the Team section replaces.

## Images and video

- Sources: the YouTube channel https://www.youtube.com/@SimplesmenteCapoeiraBerlin (professional
  1080p footage of Batizados 2022–2025 and rodas) and Instagram
  https://www.instagram.com/simplesmente_capoeira_berlin/.
- **For now:** use stills taken from the YouTube videos (max-res thumbnails, or frames grabbed at
  1080p) and the existing `assets/media/welcome.jpg` and `SC_example_horda.jpeg`. Good candidates
  found so far:
  - `dm_Bwea-thM`: a kick over a ducking player in a hall with arched windows
  - `94x_-eeQqY4`: a mid-air au with the circle clapping
  - `5mgMGsqMNkw`: kids in SC shirts
  - `6Fk1dvp1te0`: kids training
- **Later:** the club swaps in original high-res photos. Images must therefore be simple to
  replace: files in the repo, referenced from front matter, with Hugo resizing them.
- **Consent:** many frames show children. The user confirmed that parents' photo consent covers
  the website, so kids photos may be used from the first release.

## How it gets made (decided)

- Build on the existing Hugo + HugoBlox setup. Use custom landing-page blocks and partials in
  `layouts/`, plus styles in `assets/scss/template.scss` (a `custom.scss` does not load). The
  homepage content stays in front matter (`sections:`) of both `_index.md` files, so content and
  translations stay editable as content, not hard-coded in templates.
- EN and DE are changed together (see `CLAUDE.md`).
- Work on a branch and open a PR to `main`. Another maintainer merges. Run `hugo --minify` before
  the PR.

## Left to the builder

- Exactly how to extend or override HugoBlox: custom `layouts/partials/blocks/*` vs. overriding
  theme partials, and how to restyle the header and footer.
- The exact font, sizes, spacing and breakpoints, within the look of the approved mockup.
- Whether the training times live in one data file (e.g. `data/trainings.yaml`) or one front-matter
  list. It must be a single source, used by the strip, the training cards, the kids section **and
  the JSON-LD** in `layouts/partials/custom_head.html`. That file currently hard-codes the times
  and addresses in `openingHoursSpecification` and in the FAQPage answers. Generate those parts
  from the same source, keeping the schema otherwise as it is (my call). The data model needs
  whatever schema.org fields that takes (weekday, opens/closes, district).
- FAQPage JSON-LD answers must stay visible on the page (Google requirement). Collapsed
  `<details>` text counts. The FAQ content stays on the homepage.
- Which video stills go where.
- How to keep the SEO text: shorter copy, a collapsed "More about capoeira in Berlin", or moving
  it into the sections. Keep the `seo:` front matter and JSON-LD as they are.
- Dark mode: the new look is white-first. Removing the day/night toggle is acceptable.

## Reference

The approved mockups (local only, not committed) are in
`.superpowers/brainstorm/*/content/hero.html` (option B) and `homepage.html`.
