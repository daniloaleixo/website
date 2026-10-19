# Simplesmente Capoeira Berlin e.V. website
derived from [Hugo Research Group Theme](https://github.com/wowchemy/starter-hugo-research-group)

![Screenshot](preview.png)

## developer notes

For costumization add scss code in [./assets/scss/template.scss](./assets/scss/template.scss)
* **failed attempt custom.scss**: I tried creating a new file `./assets/scss/costume.scss` but it is not imported even though according to `hugo mod graph` the github.com/HugoBlox/hugo-blox-builder/modules/blox-bootstrap/v5@ is used and according to their [assets/scss/main.scss](https://github.com/HugoBlox/hugo-blox-builder/blob/main/modules/blox-bootstrap/assets/scss/main.scss) `template` and `costum` are imported ... still `costum.scss` does not work

* **Training times and locations** live in [./data/trainings.toml](./data/trainings.toml). The homepage strip, the training cards, the kids section, the FAQ answers and the JSON-LD all read them from there.
* **FAQ questions and answers** (EN and DE) live in [./data/faq.toml](./data/faq.toml).
* **Tests:** `python3 scripts/test_site.py` builds the site and checks the homepage (needs Hugo and Python 3.11+).

## usefull links for developing 

[![Get Started](https://img.shields.io/badge/-Get%20started-ff4655?style=for-the-badge)](https://hugoblox.com/hugo-themes/)
[![Discord](https://img.shields.io/discord/722225264733716590?style=for-the-badge)](https://discord.com/channels/722225264733716590/742892432458252370/742895548159492138)  
[![Twitter Follow](https://img.shields.io/twitter/follow/GetResearchDev?label=Follow%20on%20Twitter)](https://twitter.com/wowchemy)

Easily write technical content with plain text Markdown, LaTeX math, diagrams, RMarkdown, or Jupyter, and import publications from BibTeX.

[Check out the latest demo](https://research-group.netlify.app/) of what you'll get in less than 60 seconds, or [view the showcase](https://hugoblox.com/creators/).

The integrated [**Wowchemy**](https://hugoblox.com) website builder and CMS makes it easy to create a beautiful website for free. Edit your site in the CMS (or your favorite editor), generate it with [Hugo](https://github.com/gohugoio/hugo), and deploy with GitHub or Netlify. Customize anything on your site with widgets, light/dark themes, and language packs.

- 👉 [**Get Started**](https://hugoblox.com/hugo-themes/)
- 📚 [View the **documentation**](https://docs.hugoblox.com/)
- 💬 [Chat with the **Wowchemy research community**](https://discord.gg/z8wNYzb) or [**Hugo community**](https://discourse.gohugo.io)
- ⬇️ **Automatically import citations from BibTeX** with the [Hugo Academic CLI](https://github.com/GetRD/academic-file-converter)
- 🐦 Share your new site with the community: [@wowchemy](https://twitter.com/wowchemy) [@GeorgeCushen](https://twitter.com/GeorgeCushen) [#MadeWithWowchemy](https://twitter.com/search?q=%23MadeWithWowchemy&src=typed_query)
- 🗳 [Take the survey and help us improve #OpenSource](https://forms.gle/NioD9VhUg7PNmdCAA)
- 🚀 [Contribute improvements](https://github.com/HugoBlox/hugo-blox-builder/blob/main/CONTRIBUTING.md) or [suggest improvements](https://github.com/HugoBlox/hugo-blox-builder/issues)
- ⬆️ **Updating?** View the [Update Guide](https://docs.hugoblox.com/hugo-tutorials/update/) and [Release Notes](https://github.com/HugoBlox/hugo-blox-builder/releases)