---
name: add-event
description: Create a new event page (Batizado, workshop, roda) in both English and German. Use when the user wants to announce or add an event to the site.
---

Events are page bundles at `content/<lang>/event/<slug>/index.md` with an optional
`featured.png`/`featured.jpg` beside it. Model new ones on the latest existing event (e.g.
`content/en/event/batizado2026/` and `content/de/event/batizado2026/`).

1. Get from the user: title, dates/times, location(s) and address, short summary, featured
   image (path), and any videos. Ask for what's missing; don't invent dates or addresses.
2. Pick a slug following the existing pattern (`batizado2027`, …).
3. Copy the latest event's `index.md` into `content/en/event/<slug>/` and fill in:
   `title`, `seo.title`, `seo.description`, `location`, `address.street` (Google Maps link,
   HTML-escaped `&amp;` as in the existing file), `summary`, `abstract`, `date`, `date_end`
   (ISO, `Z` suffix as in existing events), `publishDate` (when the page goes live), and the
   body (`## Program`, `{{< youtube <id> >}}` embeds).
4. Create the German version at `content/de/event/<slug>/index.md`: same front matter
   structure and dates, text translated to German, internal links prefixed with `/de/`.
5. Put the featured image in **both** bundles.
6. Run `hugo --minify` if Hugo is installed and check the page under `/event/<slug>/` and
   `/de/event/<slug>/`. Then branch, commit, and open a PR (don't push to `main`).
