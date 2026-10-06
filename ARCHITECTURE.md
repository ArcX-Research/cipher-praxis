# Cipher Praxis — A Dilate Cryptography Knowledge Base

Architecture and content-schema note. Read this before adding content or code.

## 1. Purpose and scope

Cipher Praxis is a public, general-cryptography knowledge base. It preserves and explains the
classical-cipher models, algebra, cryptanalysis techniques, statistical instruments, search and
exact solvers, validation protocols, and engineering practice supported by standard literature
and the local cryptanalytic research archives.

The repository is the **evidence corpus**, not the subject. Public content is written as general
cryptography research:

- No puzzle names, puzzle numbering, contest names, ciphertexts, plaintexts, hints, or operational
  puzzle detail appear in any public field. A build-time lint (`build.rs`) rejects forbidden
  tokens in public fields.
- Internal provenance (`[[provenance]]`) may cite project files, log ids, and audit notes so that
  every claim is traceable. The Evidence panel leads with literature and puts archival paths
  inside a "Supporting research records" disclosure. Provenance is exempt from the public-text
  lint (file names may contain internal identifiers).
- Results are reported as they were recorded: planted-control pass rates, power numbers, null
  distributions, throughput. Nothing is invented; missing evidence is `UNTESTED`.

## 2. Information architecture (public)

| Route | Section id | What it holds |
| --- | --- | --- |
| `/` | — | Overview: what the knowledge base is, how to read statuses, entry points |
| `/ciphers` | `ciphers` | Cipher Systems: families and individual cipher models |
| `/algebra` | `algebra` | Mathematical Foundations: the algebra and number theory used by the models and solvers |
| `/cryptanalysis` | `cryptanalysis` | Cryptanalysis (attack strategies) |
| `/statistics` | `statistics` | Statistical Analysis (estimators, nulls, evidence) |
| `/search` | `search` | Search Methods: heuristic search and optimization |
| `/exact` | `exact` | Exact Solvers: CSP, CP-SAT/SMT, DP, exhaustive enumeration |
| `/validation` | `validation` | Validation (planted controls, power, audits, receipts) |
| `/engineering` | `engineering` | Solver Engineering (cores, harnesses, reproducibility) |
| `/labs` | `labs` | Interactive cipher and analysis labs |
| `/glossary` | `glossary` | Terms |
| `/references` | `references` | Sources: literature and the internal evidence corpus |
| `/<section>/<id>` | — | Entry page for any record |

Every method page follows the same block order where applicable: definition, equations, variants,
assumptions & invariants, attack strategy, optimized pseudocode, complexity, failure modes, controls, reproducible generic
example, notes. Blocks are optional but the *kind* vocabulary is fixed (see §4).

## 3. Stack decision

Checked tools: `rustc`/`cargo` 1.95 with the `wasm32-unknown-unknown` target installed,
`wasm-bindgen` CLI 0.2.127, `wasm-pack` 0.13.1, Node 22, Bun; `trunk` and `wasm-opt` are not
installed and crates.io is reachable.

Decision: **Rust + Leptos 0.8 (client-side rendering) compiled to WebAssembly**, built with
`cargo build --target wasm32-unknown-unknown` and the installed `wasm-bindgen` CLI (pinned to the
same version in `Cargo.toml`). No Trunk dependency: one shell script builds, one serves. Rationale:

- The dependency lockfile and version checks constrain the build inputs. Byte-for-byte
  reproducibility still needs a recorded comparison under the same toolchain, environment,
  content, and optional optimization settings.
- Leptos gives fine-grained reactivity, a typed router, and small binaries; the whole UI, the
  search index, the Markdown+math renderer and the cipher labs run in WASM.
- The cipher and statistics code lives in `crates/core/src/crypto` with unit tests
  that run natively (`cargo test`), independent of the web layer.

Rendering pipeline: content TOML → `build.rs` (validate, lint, bundle to JSON) → `include_str!` →
`serde_json` at startup → in-memory indexes → Leptos views. Markdown is rendered with
`pulldown-cmark` (math extension enabled); `$…$`/`$$…$$` spans are converted to MathML with
`pulldown-latex` and rendered natively by the browser (no external JS, no KaTeX).

## 4. Content schema (`content/<section>/<id>.toml`)

One TOML file per entry. Fields:

```toml
id = "vigenere"                 # slug, unique across ALL sections; the URL is /<section>/<id>
section = "ciphers"             # ciphers | algebra | cryptanalysis | statistics | search | exact
                                # | validation | engineering | labs | glossary | references
title = "Vigenère cipher"
subtitle = "Periodic additive substitution over Z26"       # optional, one line
status = "VERIFIED"             # VERIFIED | PROMISING | CLOSED | POWER-LIMITED | INCONCLUSIVE | UNTESTED
status_note = "One or two sentences saying what the status rests on."
family = "Polyalphabetic substitution"   # taxonomy / topic group used for filtering and grouping
tags = ["periodic", "additive"]
related = ["beaufort", "index-of-coincidence"]   # ids of other entries (validated at build time)
summary = "One plain-language paragraph. Searchable."
updated = "2026-09-04"
lab = "vigenere"                # labs only: the Rust lab component key

[[blocks]]                      # ordered page blocks
kind = "definition"             # definition | equations | variants | assumptions | attack | pseudocode
                                # | complexity | failure_modes | controls | example | notes | history
title = "Definition"            # optional; defaults to the kind's display name
body = '''Markdown with $inline$ and $$display$$ LaTeX.'''

[[provenance]]                  # internal evidence (rendered in the Evidence panel)
path = "withmath/wm_core.py"    # repository-relative path
kind = "solver"                 # solver | library | audit | design | note | log | script | data | ledger
note = "Exact period alignment over all shift vectors"
ref = "LOG01"                   # optional ledger/log identifier

[[references]]                  # external literature
title = "The Codebreakers"
author = "David Kahn"
year = 1967
url = "https://…"               # optional
```

Unprefixed provenance paths resolve under `../Cryptanalysis`, falling back to the relocated
`Cryptanalysis` directory inside the research root when the adjacent checkout is absent. `archive-a/`, `archive-b/` and
`archive-c/` resolve under the additional local research collections; `CipherPraxis/` resolves
under this repository. `scripts/check_provenance.py` accepts overrides for all five roots. These aliases
are archival identifiers and do not define the public subject or taxonomy of an article.

Status vocabulary (rendered as badges; the Overview explains them):

- `VERIFIED` — the stated claim has a cited derivation or recorded validation. The status note
  identifies the assumptions, evidence, and scope; the badge does not imply independent peer review.
- `PROMISING` — positive evidence exists but matched controls or audits are incomplete.
- `CLOSED` — a completed search or test produced a documented negative result within a declared
  scope. The entry distinguishes exact exclusion from statistical evidence or a bounded search miss.
- `POWER-LIMITED` — measured recovery or detection was insufficient under the tested conditions
  and budget. A miss gives limited evidence of absence; this is not a proof of impossibility.
- `INCONCLUSIVE` — mixed evidence, unresolved audit, or invalidated run.
- `UNTESTED` — documented but not exercised.

Editorial rules for public fields (`title`, `subtitle`, `summary`, `status_note`, `tags`, `family`,
block `title`/`body`, glossary text):

1. General cryptography only. Forbidden tokens (lint-enforced, case-insensitive, word-bounded):
   `kryptos`, `ctf`, `sanborn`, `langley`, `cia`, `pk1`…`pk10`, `pk89`, `pk98`, `pk8910`, `k1`…`k4`
   as puzzle labels, `leaderboard`, `submission`.
2. Never quote a live ciphertext, plaintext, hint, or crib list. Examples must be generic and
   reproducible (a stated plaintext of your own, a stated key, the resulting ciphertext).
3. Empirical numbers need a receipt (a log, audit, or note named in `[[provenance]]`).
   Mathematical values and synthetic examples need a derivation or mathematical source.
4. Say what a negative means: scope, text length, control power.

## 5. Brand (Dilate, light theme only)

Derived from the Dilate visual language, with restrained scientific reading surfaces:

- Ink uses Dilate navy `#000020`; body ink `#545368`; muted ink
  `#656579`; Dilate blue `#0454ff`. Reading surfaces are white `#ffffff`, with neutral
  `#f6f6f9`/`#eeeef4` accents and `#e3e3eb` borders. The sidebar uses light gray `#f6f6f7`,
  dark text, neutral hover/selection backgrounds, and a blue active marker.
  The navbar stays white, with search at its right edge.
  The desktop sidebar reaches the top of the viewport and holds the site identity.
  On mobile, the white navbar shows the identity while the sidebar becomes a full-height drawer.
  Article content and its right rail share a centered, width-limited layout within the
  workspace, with evidence and citation sections aligned to the same outer edges.
- Type is taken from the Dilate Framer project: Adamina 400 for display, page, card,
  and article headings; Geist 400/500/600 for UI and body; DM Mono 400/500 for data/code.
  Article body follows the 18 px / 30 px, −0.02em preset; article headings use 40/32/26 px
  with responsive sizing, 1.25–1.35 line-height, and −0.03em/−0.02em tracking.
  The hero uses Adamina up to 64 px, 1.2 line-height, and −0.04em tracking.
  Radii remain 8/12/20 px.
- Titles and headings have no trailing periods. Questions retain their question marks.
- Keep page backgrounds, footers, cards, filter panels, and lab outputs white. Avoid
  decorative page-wide dots, gradients, or translucent reading surfaces. The hero SVG
  retains its original blue/teal artwork. Other accents, marks, and charts use navy and
  blue; research statuses always have text labels and restrained borders. Red is reserved
  for actual input or rendering errors. No dark mode.
- Omit search-readiness messages, section ordinal numbers, redundant result-count lines,
  and build/stack details. Filter results remain announced to assistive technology.
- The overview pairs a concise introduction with a transparent vector security illustration in
  blue and teal. The text column stops growing at 640 px; the artwork is centered in the remaining
  space and its faint halo fades into the page. On wide screens the communication chain extends
  left while the main shield stays in place; smaller layouts fit the full illustration to its column.
  The introduction begins 20–32 px below the header. Subject cards use one short description;
  suggested entries and labs link to canonical pages without repeating their metadata and tags.
  The six evidence definitions remain visible, with reading principles open by default in a
  disclosure. Article headers separate parent
  navigation, family and the semantic update date. Responsive overview grids use workspace
  container queries so the left navigation is included in available-width calculations.
- Category indexes use aligned entry rows and a 300 px right sidebar for search, family,
  topic, grouping, and evidence status. All eleven categories share the filter logic;
  Glossary retains its definitions and letter index, and References retains bibliographies.
  Topics are counted once per entry, grouped without regard to case, and alphabetized.
  Full search uses the same row layout and tools rail. Below 920 px of available workspace,
  the rail becomes an expandable panel between the heading and results.
- Labs share sentence-case labels, associated input hints, quiet output panels and a static
  activity marker. The affine lab pairs encryption with recovered plaintext, shows the first
  letter's arithmetic and offers accessible multiplier buttons with their modular inverses.
  Lab container queries keep inputs, output comparisons and the key selector readable at
  the article column's actual width. Shared field grids align labels, controls and helper
  text on separate tracks; result cards share label and value tracks as well. Three-field
  rows stack together on narrow screens, and four-result comparisons become two columns.

## 6. Layout of this directory

```
CipherPraxis/
  ARCHITECTURE.md      this note
  README.md            run/build instructions
  Cargo.toml, Cargo.lock
  content/<section>/*.toml
  crates/core/         content model, search, Markdown+math, crypto core, validators and tests
  crates/web/          Leptos app and labs; build.rs validates and bundles the content
  static/              index.html template assets: styles.css, favicon, fonts CSS
  scripts/             build.sh, serve.py, check.sh
  dist/                build output (generated, ignored)
```
