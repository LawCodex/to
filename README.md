# LawCodex — Tonga (`to`)

Legislation of the Kingdom of Tonga as plain Markdown, in **English** (`en/`) and **Tongan**
(`to/`), taken from the current *Revised Edition* published by the Attorney General's Office
on the official legislation website <https://ago.gov.to/cms/> ("Tongan Legislation").

Part of [LawCodex](https://github.com/LawCodex): the legislation of every country as Markdown in git.

Retrieved: **2026-10-13** (point-in-time = retrieval date).

## Contents

| Category | English (`en/`) | Tongan (`to/`) |
|---|---:|---:|
| Constitution (`constitution/`) | 1 | 1 |
| Principal Acts (`acts/`) | 246 | 244 |
| Subordinate legislation (`subordinate/<parent act>/`) | 209 (under 95 Acts) | 204 |
| **Total files** | **456** | **449** |

These are all principal Acts and subordinate instruments listed under *Legislation → Current
Revised Edition → by Title* (A–Z) on the AGO site, in their current version (the site's
"2020 Revised Edition" consolidation, plus later versions where the AGO has issued them).

## What is NOT covered

- **Amending Acts** (73 rows in the listing): they are incorporated (or pending incorporation)
  in the consolidated principal texts and are not reproduced separately. Note that some
  amendments made after the 2020 Revised Edition may not yet be reflected in the consolidated
  PDF of the principal Act — check the `amended by…` entries on the AGO site.
- Acts/regulations "not in force", gazettes, bills, treaties and court judgments.
- Files missing or unusable on the server at retrieval time: 6 Tongan PDFs returned HTTP 404
  (e.g. *Lao ki he Tono mo e Fe'auaki*, *Lao ki hono Malu'i 'o e Ngaahi Faka'ilonga
  Fakasiokalafi*, four subordinate instruments with empty file names), and the *Civil Aviation
  Regulations 1992* (both languages) are image-only scans (no OCR performed).
- Layout: text is extracted from the official PDFs; tables, forms and schedules are flattened
  to text, page headers/footers and the "Arrangement of Sections" (table of contents) are
  dropped. Endnote reference numbers remain attached to the text (e.g. `...Cabinet.3`), with the
  endnotes themselves at the end of each file under `## Endnotes`.

## Structure

```
en/constitution/1988-0002-constitution-of-tonga.md
en/acts/<item number>-<slug>.md                 en/acts/1924-0010-criminal-offences-act.md
en/subordinate/<parent item>-<parent slug>/<item number>-<slug>.md
to/...                                          same layout, Tongan text (title_en in front matter)
```

`identifier` is the AGO "item number" (`YYYY-NNNN`, e.g. `1990-0027` = Act 27 of 1990).
Headings: `## PART …`, `### Division …`, `#### <section number> <section heading>`.
Front matter also records `version` (revised-edition file version), `version_commenced`,
`subject` (AGO subject category), and `parent_act` for subordinate legislation.

## Sources and licence

- Official source: Attorney General's Office of Tonga, <https://ago.gov.to/cms/legislation/current-revised-edition/by-title.html>
  (PDFs under `https://ago.gov.to/cms/images/LEGISLATION/…`). robots.txt allows these paths; no
  terms of use prohibiting automated access were found.
- The site footer reads "All Web Content © The Kingdom of Tonga — All Rights Reserved". The texts
  are official legislation of the Kingdom of Tonga, reproduced here verbatim (text only) as public
  legal information. This is **not** an official version — consult the AGO site for authoritative texts.

## Regenerate

```sh
python3 scripts/to_fetch.py   ../_raw/to          # listings A–Z + PDFs (cached, polite: 2 parallel downloads)
python3 scripts/to_convert.py ../_raw/to .        # PDF -> Markdown (needs poppler `pdftotext`)
```
