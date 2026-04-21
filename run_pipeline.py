"""
Pipeline Runner — Phase 1 only (no models).
  Step 1: build_index.py  →  index.csv
  Step 2: phase1_extract.py  →  features.csv
  Step 3: eda_report.py  →  eda_positive_only.pdf

Research use only. Experimental probability model. Not a diagnostic test.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "src"))


def main():
    print("=" * 60)
    print("PREGNANCY DETECTION AI — DATA PIPELINE")
    print("Phase 1 only. No models. No predictions.")
    print("=" * 60)

    # Step 1: Build index
    print("\n--- STEP 1: Build Index ---")
    from build_index import build_index
    build_index()

    # Step 2: Extract features
    print("\n--- STEP 2: Feature Extraction ---")
    from phase1_extract import run_extraction
    run_extraction()

    # Step 3: EDA report
    print("\n--- STEP 3: EDA Report ---")
    from eda_report import run_eda
    run_eda()

    print("\n" + "=" * 60)
    print("PIPELINE COMPLETE")
    print("Outputs:")
    print("  data/processed/index.csv")
    print("  data/processed/features.csv")
    print("  reports/eda_positive_only.pdf")
    print("=" * 60)
    print("Research use only. Experimental probability model. Not a diagnostic test.")


if __name__ == "__main__":
    main()
