#!/usr/bin/env bash
# ============================================================
# Atlas Compendium — Full Build Pipeline
# Builds master PDF + per-volume standalone PDFs, both editions.
# ============================================================

set -euo pipefail
cd "$(dirname "$0")/.."

# ── Parse args ──
EDITIONS="public private"
VOLUMES_ONLY=false
MASTER_ONLY=false
CLEAN=false
VERSION_ONLY=false

for arg in "$@"; do
  case "$arg" in
    --edition=*)   EDITIONS="${arg#--edition=}" ;;
    --volumes-only) VOLUMES_ONLY=true ;;
    --master-only)  MASTER_ONLY=true ;;
    --clean)        CLEAN=true ;;
    --version)      VERSION_ONLY=true ;;
    --help|-h)
      echo "Usage: build_all.sh [--edition=public|private] [--volumes-only] [--master-only] [--clean] [--version]"
      exit 0 ;;
  esac
done

# ── Read version from manifest ──
VERSION=$(python3 -c "import yaml; m=yaml.safe_load(open('MANIFEST.yaml')); print(m['compendium']['version'])" 2>/dev/null || echo "0.0.0")
GIT_HASH=$(git -C .. rev-parse --short HEAD 2>/dev/null || echo "unknown")
BUILD_DATE=$(date -u +%Y-%m-%d)

if [ "$VERSION_ONLY" = true ]; then
  echo "Atlas Compendium v${VERSION} (${GIT_HASH})"
  exit 0
fi

echo "Atlas Compendium Build Pipeline"
echo "  version: v${VERSION}"
echo "  git:     ${GIT_HASH}"
echo "  date:    ${BUILD_DATE}"
echo "  editions: ${EDITIONS}"
echo ""

# ── Clean ──
OUTDIR="build/output"
if [ "$CLEAN" = true ]; then
  echo "Cleaning ${OUTDIR}/..."
  rm -rf "${OUTDIR}"
fi

# ── Setup output dirs ──
for ed in $EDITIONS; do
  mkdir -p "${OUTDIR}/${ed}/research_papers"
  mkdir -p "${OUTDIR}/${ed}/positioning_essays"
  mkdir -p "${OUTDIR}/${ed}/field_dives"
  mkdir -p "${OUTDIR}/${ed}/technical_reference"
done

built=0
failed=0
skipped=0
manifest_entries="[]"

# ── Build master ──
if [ "$VOLUMES_ONLY" != true ]; then
  for ed in $EDITIONS; do
    master_out="${OUTDIR}/${ed}/atlas_compendium_v${VERSION}_${BUILD_DATE}.pdf"
    echo -n "Master (${ed}): "
    if typst compile --root "$(pwd)" --input "edition=${ed}" compendium.typ "${master_out}" 2>/tmp/typst_err.txt; then
      size=$(stat -c%s "${master_out}" 2>/dev/null || echo "?")
      echo "OK (${size} bytes)"
      built=$((built + 1))
    else
      echo "FAILED"
      cat /tmp/typst_err.txt
      failed=$((failed + 1))
    fi
  done
fi

# ── Build individual volumes ──
if [ "$MASTER_ONLY" != true ]; then
  # Read volume list from manifest
  python3 -c "
import yaml, json, sys
m = yaml.safe_load(open('MANIFEST.yaml'))
for v in m['volumes']:
    # Convert date objects to strings for JSON
    for k in list(v.keys()):
        if hasattr(v[k], 'isoformat'):
            v[k] = v[k].isoformat()
    print(json.dumps(v))
" | while IFS= read -r vol_json; do
    vol_id=$(echo "$vol_json" | python3 -c "import json,sys; print(json.load(sys.stdin)['id'])")
    vol_status=$(echo "$vol_json" | python3 -c "import json,sys; print(json.load(sys.stdin)['status'])")
    vol_editions=$(echo "$vol_json" | python3 -c "import json,sys; print(' '.join(json.load(sys.stdin)['editions']))")
    vol_kind=$(echo "$vol_json" | python3 -c "import json,sys; print(json.load(sys.stdin)['kind'])")

    src="${vol_id}.typ"
    if [ ! -f "$src" ]; then
      echo "  SKIP ${vol_id} (file not found)"
      continue
    fi

    for ed in $EDITIONS; do
      if echo "$vol_editions" | grep -qw "$ed"; then
        basename=$(basename "$vol_id")
        out="${OUTDIR}/${ed}/${vol_kind}s/${basename}_v${VERSION}.pdf"
        # Ensure subdir exists
        mkdir -p "$(dirname "$out")"
        echo -n "  ${vol_id} (${ed}): "
        if typst compile --root "$(pwd)" "$src" "$out" 2>/dev/null; then
          size=$(stat -c%s "$out" 2>/dev/null || echo "?")
          echo "OK (${size} bytes, ${vol_status})"
        else
          echo "FAILED"
        fi
      fi
    done
  done
fi

# ── Build manifest.json ──
echo ""
echo "Writing manifest.json..."
python3 << PYEOF
import json, os, yaml
from datetime import datetime

m = yaml.safe_load(open('MANIFEST.yaml'))
git_hash = "${GIT_HASH}"
build_date = "${BUILD_DATE}"
version = "${VERSION}"
outdir = "${OUTDIR}"

entries = []
for root, dirs, files in os.walk(outdir):
    for f in files:
        if f.endswith('.pdf'):
            path = os.path.join(root, f)
            size = os.path.getsize(path)
            rel = os.path.relpath(path, outdir)
            entries.append({"path": rel, "size": size})

manifest = {
    "build_date": build_date,
    "version": version,
    "git_hash": git_hash,
    "typst_version": "0.14.2",
    "editions_built": "${EDITIONS}".split(),
    "volumes_total": len(m['volumes']),
    "volumes_built": len([v for v in m['volumes'] if v['status'] == 'built']),
    "volumes_scaffold": len([v for v in m['volumes'] if v['status'] == 'scaffold']),
    "pdfs": entries,
}

with open(os.path.join(outdir, "manifest.json"), "w") as f:
    json.dump(manifest, f, indent=2, default=str)
print(json.dumps(manifest, indent=2, default=str))
PYEOF

echo ""
echo "Build complete. Output in compendium/${OUTDIR}/"
