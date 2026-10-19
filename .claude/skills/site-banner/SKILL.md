---
name: site-banner
description: Add, change, or remove the site-wide announcement bar on sc-capoeira.de (e.g. a training location closed, a schedule change). Use whenever the user wants a banner/announcement shown, updated, or taken down.
---

The banner is set in front matter of `content/en/_index.md` and `content/de/_index.md`, each
holding two blocks: `announcement` (homepage) and `cascade.announcement` (every other page).
All four blocks must stay in sync.

```yaml
# Site-wide banner (TEMPORARY – remove both `announcement` blocks after <date>)
announcement:
  id: <slug>-<yyyy>-<mm>
  text: '<markdown text>'
cascade:
  announcement:
    id: <slug>-<yyyy>-<mm>
    text: '<markdown text>'
```

## Add or change

1. Write the English text, then the German translation. Bold key facts with `**…**`.
   Links: `/contact/` in EN, `/de/contact/` in DE.
2. Put identical `id` + `text` in both blocks of each language file.
3. When changing text of an existing banner, bump the `id` (e.g. append `-v2`) so visitors who
   dismissed the old one see the new one.
4. If it's temporary, keep the `TEMPORARY – remove … after <date>` comment with the end date.
5. Styling lives under `#announcement.alert` in `assets/scss/template.scss`; only touch it if asked.

## Remove

Delete the comment, `announcement`, and `cascade` blocks from both `_index.md` files (leave
`cascade` if it holds other keys). Leave the SCSS in place for next time.

## Finish

`grep -n -A3 announcement content/*/_index.md` to confirm all four copies match. Run
`hugo --minify` if Hugo is installed. Then branch, commit, and open a PR (don't push to `main`).
