#!/usr/bin/env bash
# Build compendium volumes individually or as master.
# Usage:
#   ./build.sh                  # build everything
#   ./build.sh field_dives/01   # build one document (prefix match)
#   ./build.sh --master         # build unified master PDF (TBD)

set -euo pipefail
cd "$(dirname "$0")/.."

TARGETS=""
MASTER=false

for arg in "$@"; do
  if [ "$arg" = "--master" ]; then
    MASTER=true
  else
    TARGETS="$TARGETS $arg"
  fi
done

if [ -z "$TARGETS" ] && [ "$MASTER" = false ]; then
  TARGETS=$(find field_dives research_papers positioning_essays technical_reference -name "*.typ" -type f 2>/dev/null)
fi

built=0
failed=0

for target in $TARGETS; do
  # Support prefix matching: "field_dives/01" matches "field_dives/01_jyotish..."
  if [ ! -f "$target" ]; then
    match=$(find . -path "./${target}*" -name "*.typ" -type f 2>/dev/null | head -1)
    if [ -n "$match" ]; then
      target="$match"
    else
      echo "SKIP: no match for $target"
      continue
    fi
  fi

  out="build/$(basename "${target%.typ}.pdf")"
  echo -n "Building $target -> $out ... "
  if typst compile --root "$(pwd)" "$target" "$out" 2>/dev/null; then
    echo "OK"
    built=$((built + 1))
  else
    echo "FAILED"
    failed=$((failed + 1))
  fi
done

if [ "$MASTER" = true ]; then
  echo "Master build: TBD — requires unified master.typ"
fi

echo ""
echo "Build complete: $built built, $failed failed. PDFs in compendium/build/"
