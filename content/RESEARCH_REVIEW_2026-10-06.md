# Research integration review — 2026-10-06

This maintainer record describes a selective import into the general cryptography reference.
Research projects supply evidence; their private targets, hints, ciphertexts and candidate
plaintexts are not the subject of the new explanations. Locally developed methods are not
presented as claims of global priority.

## Scope

Discovery covered the research root at
`~/Projects/Mywork/ArcX-Research/Research/Cryptography`, including its curated toolkit index,
the relocated `Cryptanalysis` collection, later mathematical and structural studies, coordinate
constraint work, and the hash and authenticated-request tooling. Generated experiments and
checkpoints dominate the directory inventory. This was a review of selected definitions,
implementations, proofs and controls, not a claim to have read or rerun every archived file.

The catalog began with 319 entries and now has **329**. Existing uncommitted provenance-path
corrections were retained. Source paths occur in provenance and maintainer records; public
explanations use mathematical models and synthetic examples. No heavy recovery campaign,
GPU search or private-target experiment was run for this import.

`RESEARCH_SOURCE_INDEX_2026-10-06.json` records selected newly cited source files, source hashes,
article associations and repaired compressed-log citations. It is an inventory of those files
as found, not a historical execution receipt. `RESEARCH_CHECKS_2026-10-06.json` separately records
the source versions and results of the two executed standalone synthetic proof modes.

## New canonical articles

| Article | Distinct material and optimized procedure |
| --- | --- |
| `ciphers/sha256` | Hash compression, full versus reduced-round semantics, sixteen-word rolling schedule, padding and byte-boundary checks |
| `ciphers/hmac` | Exact-byte authentication, cached inner and outer contexts, preserved length counters, separate freshness and state-effect contracts |
| `ciphers/aes-gcm` | Authenticated encryption, cached key/GHASH preparation, explicit 96-bit-nonce profile, verification before plaintext release |
| `ciphers/amsco` | Variable-size cell transposition, cached ragged geometry, checkerboard versus continuous-stream alternation |
| `ciphers/swagman` | Latin-square column permutations, cached inverse routes, profile-search and final-score exactness boundaries |
| `ciphers/bilinear-feedback-relation` | Cached congruence roots, exact lag-chain decoding under unary costs, noninvertible states, affine coordinate normalization |
| `algebra/finite-extension-fields` | Polynomial field arithmetic and the equivalence of nonzero field multiplication to addition in logarithm coordinates |
| `exact/symbolic-codebook-propagation` | Binary XOR-disjunction closure, ternary projection capacities and color consequences before numeric codebook completion |
| `statistics/periodic-key-marginal-likelihood` | Log-sum-exp transfer matrices for a complete uniform periodic-key average; two-period gauge normalization |
| `validation/nonce-reuse-audit` | Operation deduplication and conflict exclusion before key/nonce grouping; independent coverage and finding verdicts |

The modern primitives are standard constructions. Their pages cite the relevant NIST or RFC
specifications; the archival tooling motivates implementation checks and audit scope. The
classical transpositions cite the ACA definitions and use independently constructed examples.

## Merges instead of duplicate pages

| Existing article | Material incorporated |
| --- | --- |
| `algebra/all-different-constraints` | Closed-form ternary Hall test, proof of the exclusive-cell capacity argument, binary sufficient shortcut and generic matching fallback |
| `ciphers/digraphic-slide` | Cached directional Slidefair maps and complete small pair checks; no separate Slidefair article |
| `ciphers/autokey` | Mixed plaintext/ciphertext feedback with nonunit memory coefficients; invert only the current-symbol coefficient and preserve unknown-primer freedom |
| `algebra/conjugacy-and-gauge` | Coordinate convention normalization from 1,296 descriptions to 216 classes under an explicit common-relabeling symmetry |
| `exact/pruned-traversal-equivalence-certificates` | Equality-path implication certificates for reusing a completed exclusion, with unchanged-domain and completeness requirements |
| `engineering/kat-harness` | Binary hash boundary panels and the distinction between independent implementations and copied code on different runtimes |
| `validation/endpoint-specific-control-contracts` | Separate signature, freshness, retry and independently observed application-effect contracts |
| `search/meet-in-the-middle` | Four-layer pair joins, collision-free fixed-width signatures, crib-relative phase reuse and alias retention |

The linear-keystream crib pseudocode was also aligned with its existing equation
`cipher = sign * plaintext + key`: both crib-key initialization and final decryption now use
that same sign convention. The old pseudocode was internally using a differently signed
keystream without declaring the change.

Slidefair's previous `CLOSED` description overstated a heuristic miss as a family exclusion.
The page now marks the verified transform separately from historical recovery experiments and
their search limits. Its claimed one-letter independence was also restricted to the ordinary
rectangle case: the same-column exception depends on both coordinates.

Canonical parent articles link to the additions. Identical titles, ids and substantial copied
blocks were checked; conceptual overlap was reviewed against definitions and existing
pseudocode. New implementations of already covered methods were merged rather than counted
as new discoveries. Unfinished or target-specific variants without a distinct supported
general result remain outside this import.

## Evidence maintenance

Twelve existing citation paths referred to six logs now stored as `.gz` files. The citations
now name the compressed files; gzip reads verified each complete stream. This changes file
location, not the historical measurements. Original uncompressed hashes are recorded in the
source index for traceability.

The provenance checker and standard check commands now find the relocated `Cryptanalysis`
directory inside the research root when the older adjacent checkout is absent. Explicit
`--corpus` and `CORPUS_DIR` overrides remain available. The complete catalog's cited paths
resolve with the available archives.

## Validation and limits

`scripts/check_research_additions.py` adds 15 corpus-free checks to both `make test` and
`make check`. They compare rolling SHA-256 with `hashlib`, cached HMAC with standard HMAC,
GHASH with polynomial long division, fixed-block GCM mode vectors, hand-derived transposition
routes, field identities, bilinear DP with complete assignments, periodic evidence with complete
key sums, ternary Hall classification with generic matching, and nonce audit invariance under
record reordering. They also cover Slidefair pair bijections, nonunit feedback and coordinate
convention orbits. AES itself is not implemented or independently validated by the GCM checks.

The binary closure's synthetic mode and the ternary closure's proof mode were compiled into
temporary directories and executed without private inputs. They check that inferred relations
hold in every valid assignment of their finite fixtures and that satisfiable fixtures are never
rejected. They do not establish completeness of local propagation.

The full repository check covers formatting, script syntax, native and WebAssembly compilation
and linting, Rust tests, both finite algorithm suites, strict content validation, math delimiters,
list markers and provenance paths. Exact finite arithmetic or optimization results do not imply
general cryptanalytic recovery, and a source-level optimization is not an unmeasured speedup.

All ten new routes were also checked in an isolated headless Chrome session at desktop
1440-by-1000 and mobile 390-by-844 viewports. All twenty page checks rendered their pseudocode
without page errors, document-width overflow or MathML errors. Representative article and
mobile pseudocode screenshots were visually reviewed. The user's Chrome window was not used.
