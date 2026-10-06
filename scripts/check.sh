#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

echo "▸ format"
cargo fmt --all -- --check

echo "▸ script syntax"
for script in scripts/*.sh; do
  bash -n "$script"
done
python3 -c 'import ast, pathlib; [ast.parse(path.read_text(), filename=str(path)) for path in pathlib.Path("scripts").glob("*.py")]'
if command -v shellcheck >/dev/null 2>&1; then
  shellcheck scripts/*.sh
fi
echo "▸ asset cache regression checks"
python3 scripts/test_fingerprint_assets.py

echo "▸ clippy (workspace, native)"
cargo clippy --workspace --all-targets --all-features -- -D warnings

echo "▸ tests"
cargo test --workspace --all-features

echo "▸ finite algorithm checks"
python3 scripts/check_research_algorithms.py
python3 scripts/check_research_additions.py

echo "▸ content"
cargo run --quiet -p praxis-core --features authoring --bin praxis-check -- content --strict
echo "▸ math spans"
cargo run --quiet -p praxis-core --features authoring --bin praxis-check -- content --math | tail -1
echo "▸ list markers"
cargo run --quiet -p praxis-core --features authoring --bin praxis-check -- content --lists | tail -1
echo "▸ provenance paths"
if [ -z "${CORPUS_DIR:-}" ]; then
  CORPUS_DIR="../Cryptanalysis"
  if [ ! -d "$CORPUS_DIR" ]; then
    CORPUS_DIR="$HOME/Projects/Mywork/ArcX-Research/Research/Cryptography/Cryptanalysis"
  fi
fi
if [ -d "$CORPUS_DIR" ]; then
  python3 scripts/check_provenance.py --corpus "$CORPUS_DIR"
else
  echo "provenance: skipped (corpus not found at $CORPUS_DIR)"
fi

echo "▸ clippy (web, wasm32)"
cargo clippy -p praxis-web --target wasm32-unknown-unknown -- -D warnings

echo "▸ check (web, wasm32)"
cargo check -p praxis-web --target wasm32-unknown-unknown

if [ "${REPRO:-0}" = "1" ]; then
  echo "▸ reproducibility: two clean release builds must hash identically"
  scripts/build.sh release >/dev/null
  H1="$(shasum -a 256 dist/pkg/*_bg.wasm | cut -d' ' -f1)"
  cargo clean -p praxis-web --release --target wasm32-unknown-unknown >/dev/null 2>&1
  scripts/build.sh release >/dev/null
  H2="$(shasum -a 256 dist/pkg/*_bg.wasm | cut -d' ' -f1)"
  if [ "$H1" != "$H2" ]; then
    echo "reproducibility FAILED: $H1 != $H2" >&2
    exit 1
  fi
  echo "  identical: $H1"
fi

echo "✓ all checks passed"
