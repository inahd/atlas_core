"""
Verification script: reproduces the headline result and checks it.

Run this from the packet root or from the code/ directory:
    python3 verify_result.py

Expected output:
    Ashtadhatu precision: 91.7%
    Ashtadhatu recall: 91.7%
    HEADLINE RESULT VERIFIED.

If you see different numbers, something has changed in the encoding or
data and should be investigated.
"""

import os
import sys

# Add code directory to path
script_dir = os.path.dirname(os.path.abspath(__file__))
code_dir = os.path.join(script_dir, 'code')
if os.path.isdir(code_dir):
    sys.path.insert(0, code_dir)
else:
    # Running from inside code/ directory
    sys.path.insert(0, script_dir)

from panchaloha_alloy import (
    ASHTADHATU, PANCHALOHA,
    predict_alloy_optimal_nakshatras,
    compare_framework_vs_tradition,
)


def main():
    print("=" * 70)
    print("ATLAS RESEARCH PACKET — VERIFICATION SCRIPT")
    print("=" * 70)
    print()
    print("Reproducing headline result: framework prediction vs tradition")
    print("for ashtadhatu and panchaloha sacred alloys.")
    print()

    # === Ashtadhatu (the headline result) ===
    print("Running ashtadhatu analysis...")
    ashta_predictions = predict_alloy_optimal_nakshatras(
        recipe=ASHTADHATU,
        day_of_week="thursday",
        hora_index=0,
        tithi=10,
        yoga_name="Siddha",
    )

    ashta_comparison = compare_framework_vs_tradition(
        recipe=ASHTADHATU,
        framework_predictions=ashta_predictions,
        top_n=12,
    )

    ashta_precision = ashta_comparison['precision']
    ashta_recall = ashta_comparison['recall']

    print(f"\nAshtadhatu top-12 framework predictions:")
    for i, p in enumerate(ashta_predictions[:12]):
        in_trad = "✓" if p['is_in_pratishtha_list'] else "✗"
        print(f"  #{i+1:2d} {p['nakshatra']:<22} {p['combined_score']:+.3f}  {in_trad}")

    print(f"\n  PRECISION: {ashta_precision:.1%}")
    print(f"  RECALL:    {ashta_recall:.1%}")
    print(f"  Overlap with tradition: {ashta_comparison['overlap_count']}/{ashta_comparison['tradition_count']}")

    # === Panchaloha (the secondary result demonstrating weighting matters) ===
    print()
    print("Running panchaloha (mass-weighted) analysis...")
    pancha_predictions = predict_alloy_optimal_nakshatras(
        recipe=PANCHALOHA,
        day_of_week="thursday",
        hora_index=0,
        tithi=10,
        yoga_name="Siddha",
    )
    pancha_comparison = compare_framework_vs_tradition(
        recipe=PANCHALOHA,
        framework_predictions=pancha_predictions,
        top_n=12,
    )

    print(f"  PRECISION: {pancha_comparison['precision']:.1%}")
    print(f"  RECALL:    {pancha_comparison['recall']:.1%}")
    print(f"  (Lower because heavy copper biases toward Mars-friendly nakshatras)")

    # === Verification ===
    print()
    print("=" * 70)
    print("VERIFICATION CHECK")
    print("=" * 70)

    expected_min = 0.90  # 91.7% ± measurement
    if ashta_precision >= expected_min and ashta_recall >= expected_min:
        print(f"\n  ✓ HEADLINE RESULT VERIFIED")
        print(f"    Ashtadhatu match >= {expected_min:.0%}")
        print(f"    Actual: precision {ashta_precision:.1%}, recall {ashta_recall:.1%}")
        print(f"\nThe classical Shilpa Shastra prescriptions for auspicious nakshatras")
        print(f"for ashtadhatu murti pratishtha are recoverable from BPHS")
        print(f"graha-friendship rules applied to the multi-metal composition.")
        return 0
    else:
        print(f"\n  ✗ VERIFICATION FAILED")
        print(f"    Expected match >= {expected_min:.0%}")
        print(f"    Got: precision {ashta_precision:.1%}, recall {ashta_recall:.1%}")
        print(f"\nSomething has changed in the encoding. Investigate.")
        return 1


if __name__ == '__main__':
    sys.exit(main())
