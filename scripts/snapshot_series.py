#!/usr/bin/env python3
"""Automated snapshot series for Atlas S4.

Usage:
  python3 scripts/snapshot_series.py bloom
  python3 scripts/snapshot_series.py aligned --k 12.0
  python3 scripts/snapshot_series.py merkaba
  python3 scripts/snapshot_series.py all

Creates: research/snapshots/{mode}_{timestamp}/
Takes one snapshot per tithi 1-15.

Requires: pip install playwright && playwright install chromium
"""

import argparse
import os
import sys
import time
from datetime import datetime
from pathlib import Path

try:
    import requests
except ImportError:
    print("pip install requests")
    sys.exit(1)

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    print("pip install playwright && playwright install chromium")
    sys.exit(1)

BASE = "http://localhost:5000"

NITYA = {
    1: "Kamesvari", 2: "Bhagamalini", 3: "Nityaklina",
    4: "Bherunda", 5: "Vahnivasini", 6: "Mahavajresvari",
    7: "Sivaduti", 8: "Tvarita", 9: "Kulasundari",
    10: "Nitya", 11: "Nilapataka", 12: "Vijaya",
    13: "Sarvamangala", 14: "Jvalamalini", 15: "Chidagni",
}


def run_series(mode, tithis, k_value=None, wait_ms=2000):
    ts = datetime.now().strftime("%Y%m%d_%H%M")
    folder = Path(f"research/snapshots/{mode}_{ts}")
    folder.mkdir(parents=True, exist_ok=True)

    print(f"✦ Snapshot series: {mode}")
    print(f"  output: {folder}")
    if k_value:
        print(f"  k = {k_value}")

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.set_viewport_size({"width": 1400, "height": 900})

        # Navigate to S4
        page.goto(f"{BASE}/s4")
        page.wait_for_timeout(3000)

        # Click mode button
        btn_id = f"btn-{mode}"
        try:
            page.click(f"#{btn_id}")
            page.wait_for_timeout(500)
        except Exception:
            print(f"  warning: could not click #{btn_id}")

        # Set k value if specified (via slider)
        if k_value is not None:
            try:
                page.evaluate(f"document.getElementById('k-slider').value={k_value};"
                              f"document.getElementById('k-slider').dispatchEvent(new Event('input'));")
                page.wait_for_timeout(300)
            except Exception:
                pass

        for tithi in tithis:
            devi = NITYA.get(tithi, f"t{tithi}")

            # Override field tithi via /field/override
            try:
                requests.post(f"{BASE}/field/override",
                              json={"panchanga": {"tidx": tithi, "tithi": devi}},
                              timeout=5)
            except Exception:
                pass

            # Also set tithi via slider on page
            try:
                page.evaluate(f"document.getElementById('tithi-slider').value={tithi};"
                              f"document.getElementById('tithi-slider').dispatchEvent(new Event('input'));")
            except Exception:
                pass

            page.wait_for_timeout(wait_ms)

            fname = f"tithi_{tithi:02d}_{devi.lower()}.png"
            path = str(folder / fname)
            page.screenshot(path=path)
            print(f"  ✓ tithi {tithi:2d} {devi}: {fname}")

        # Clear override
        try:
            requests.delete(f"{BASE}/field/override", timeout=5)
        except Exception:
            pass

        browser.close()

    print(f"\n✦ Done. {len(tithis)} snapshots in {folder}")
    return folder


def main():
    parser = argparse.ArgumentParser(description="Atlas S4 snapshot series")
    parser.add_argument("mode", choices=["bloom", "aligned", "merkaba", "yantra", "all"],
                        help="Which S4 mode to capture")
    parser.add_argument("--k", type=float, default=None, help="Spatial frequency k value")
    parser.add_argument("--tithis", default="1-15", help="Tithi range (e.g. 1-15 or 1,3,6,7,11,15)")
    parser.add_argument("--wait", type=int, default=2000, help="Wait ms per snapshot")
    args = parser.parse_args()

    # Parse tithis
    if "-" in args.tithis:
        start, end = args.tithis.split("-")
        tithis = list(range(int(start), int(end) + 1))
    else:
        tithis = [int(x) for x in args.tithis.split(",")]

    if args.mode == "all":
        for mode in ["bloom", "aligned", "merkaba"]:
            run_series(mode, tithis, k_value=args.k, wait_ms=args.wait)
    else:
        run_series(args.mode, tithis, k_value=args.k, wait_ms=args.wait)


if __name__ == "__main__":
    main()
