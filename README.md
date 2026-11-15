# Interactive Japanese Verb & Adjective Chart

A single-file web app (`index.html`) that redraws Aeron Buchanan's one-page Japanese
Verb Chart and makes it interactive:

- **Verbs page** – the poster layout (辞書形, 連用形, 未然形, 命令形, 推量形, 仮定形, テ形, タ形),
  every line conjugated live for the chosen verb (godan, ichidan, する, 来る, special cases,
  or any verb you type), plus ~450 grammar patterns grouped by the verb form they attach to.
- **Adjectives page** (`#adjectives`) – い-adjective and な-adjective tables (plain/polite),
  copula table, notes on irregulars, and ~70 extra adjective patterns.
- JLPT N5–N1 badge on every line and a level filter; tap any line for an explanation and
  an example sentence; Patterns view, romaji, zoom/pan.

Open `index.html` in a browser – no build step, no dependencies (fonts load from Google Fonts).

## Repository layout

| Path | What it is |
|---|---|
| `index.html` | The app (HTML + CSS + JS, data inlined) |
| `scripts/extract.py` | Pulls verb-attaching grammar points out of the two datasets below |
| `scripts/dedupe.py` | Drops patterns already on the chart (renders with Playwright to compare) |
| `scripts/adj_extract.py` | Pulls adjective-attaching grammar points |
| `data/verb_patterns.json` | Extracted verb patterns that were merged into `index.html` |
| `data/adj_patterns.json` | Extracted adjective patterns |

The generated data is already inlined in `index.html`; the scripts and JSON are kept so the
extraction can be re-run or audited. Script inputs: clone the two datasets below, then
`python3 scripts/extract.py <grammar.json> <openjlpt grammar dir> out.json`.

## Sources & licence

- Layout adapted from **Aeron Buchanan's Japanese Verb Chart v3.0** (CC BY-SA 3.0) –
  https://commons.wikimedia.org/wiki/File:AMB_Japanese_Verbs.pdf
- Grammar points and levels: **Japanese Language Data** (jkindrix, CC BY-SA 4.0) –
  https://github.com/jkindrix/japanese-language-data and **OpenJLPT** (CC BY-SA 4.0) –
  https://github.com/evanclan/OpenJLPT; levels cross-checked against JLPT Sensei's lists.
- There is no official JLPT grammar list; levels are community consensus.

This work is released under **CC BY-SA 4.0** (https://creativecommons.org/licenses/by-sa/4.0/).
