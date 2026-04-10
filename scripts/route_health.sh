#!/bin/bash
# Route health check — run before and after each blueprint extraction.
# Output must be identical across extractions.

ROUTES="/field /goloka /helix /trajectory /rings /yantra /guild/state \
        /sound/spec /corpus/search?q=nakshatra /layers /dinacharya \
        /glyphs/all /system/state /reading/bandhu /card/deck/atlas \
        /health /symbols/stats /dashboard/health /render/eternal \
        /plants/catalog /research/gaps /land /corpus/registry"

echo "Route health check ($(date '+%Y-%m-%d %H:%M:%S')):"
PASS=0
FAIL=0
for route in $ROUTES; do
  code=$(curl -s -o /dev/null -w '%{http_code}' --max-time 5 "localhost:5000$route")
  if [ "$code" = "200" ]; then
    status="✓"
    PASS=$((PASS + 1))
  else
    status="✗ $code"
    FAIL=$((FAIL + 1))
  fi
  printf "  %-40s %s\n" "$route" "$status"
done
echo ""
echo "Total: $((PASS + FAIL))  Pass: $PASS  Fail: $FAIL"
