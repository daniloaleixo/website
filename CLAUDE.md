# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

Hugo site for Simplesmente Capoeira Berlin e.V. (sc-capoeira.de), built on HugoBlox theme modules
pulled in through `go.mod` / `config/_default/module.yaml`. No npm, no tests, no linter.

## Commands

- Requires Hugo **0.160.1 extended** (pinned in `.github/workflows/publish.yaml` and `netlify.toml`).
- Dev: `hugo server`. Production build (as CI): `hugo --minify`; run it before opening a PR.
  The `.Site.Data` / `.Site.AllPages` deprecation and `sitemap.xml` render-hook warnings come from
  the theme and are expected.

## Content is bilingual

- `content/en/` (default, served at `/`) and `content/de/` (served at `/de/`) are mirrored trees.
  Every content change goes into **both**, at the same path, including page-bundle images.
- Write the German version yourself; don't leave English text in `content/de/`.
- Internal links in DE content must carry the `/de/` prefix (`/de/contact/`, not `/contact/`).
- Menus in `config/_default/menus.yaml` are shared by both languages.

## Gotchas

- Custom styles go in `assets/scss/template.scss`; a `custom.scss` does not load.
- Raw HTML in Markdown is enabled (`goldmark unsafe: true`).
- The site-wide banner is `announcement` **and** `cascade.announcement` in both `_index.md` files
  (4 identical copies). Use `/site-banner` to change it.

## Git

- Work on a feature branch and open a PR to `main`; never push to `main` directly. Another
  maintainer merges. Pushing to `main` deploys to GitHub Pages.
