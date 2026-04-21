"""
Model Promotion — Manual Production Deployment
After reviewing a new model's metrics, run this to promote it to production.

Usage:
    python src/promote_model.py --filename model_B_v2_20260422.pkl
    python src/promote_model.py --list              # Show all models
    python src/promote_model.py --latest hand_coded  # Promote latest of a type

What "production" means:
  - The API loads this specific model file on next restart
  - registry.json marks this version as current
  - The previous production model is archived but kept on disk

Research use only. Experimental probability model. Not a diagnostic test.
"""

import os
import sys
import json
import argparse
from datetime import datetime

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODELS_DIR = os.path.join(PROJECT_ROOT, "models")
REGISTRY_PATH = os.path.join(MODELS_DIR, "registry.json")
DISCLAIMER = "Research use only. Experimental probability model. Not a diagnostic test."


def load_registry():
    if os.path.exists(REGISTRY_PATH):
        with open(REGISTRY_PATH, "r") as f:
            return json.load(f)
    return {"models": [], "production": {"hand_coded": None, "cnn": None}}


def save_registry(registry):
    with open(REGISTRY_PATH, "w") as f:
        json.dump(registry, f, indent=2)


def list_models(registry):
    """Print all registered models."""
    print("=" * 80)
    print("MODEL REGISTRY")
    print("=" * 80)

    if not registry["models"]:
        print("  No models registered yet.")
        print("  Run retrain.py after adding NEGATIVE data.")
        return

    prod_hc = registry["production"].get("hand_coded")
    prod_cnn = registry["production"].get("cnn")

    print(f"\n{'Filename':<45} {'Type':<13} {'AUC':>6} {'Subjects':>9} {'Date':<20} {'Status'}")
    print("-" * 110)

    for entry in sorted(registry["models"], key=lambda e: e.get("trained_at", ""), reverse=True):
        filename = entry["filename"]
        model_type = entry.get("type", "unknown")
        auc = entry.get("mean_auc", 0)
        n_subj = entry.get("n_subjects", 0)
        trained = entry.get("trained_at", "")[:19]

        status = ""
        if filename == prod_hc:
            status = "<-- PRODUCTION (hand_coded)"
        elif filename == prod_cnn:
            status = "<-- PRODUCTION (cnn)"

        print(f"  {filename:<43} {model_type:<13} {auc:>6.4f} {n_subj:>9} {trained:<20} {status}")

    print()
    print(f"Production hand_coded: {prod_hc or '(none)'}")
    print(f"Production cnn:        {prod_cnn or '(none)'}")


def promote(registry, filename):
    """Promote a specific model to production."""
    # Find the model in registry
    entry = None
    for e in registry["models"]:
        if e["filename"] == filename:
            entry = e
            break

    if entry is None:
        print(f"ERROR: Model '{filename}' not found in registry.")
        print("Run --list to see available models.")
        return False

    # Check file exists on disk
    model_path = os.path.join(MODELS_DIR, filename)
    if not os.path.exists(model_path):
        print(f"ERROR: Model file not found on disk: {model_path}")
        return False

    model_type = entry.get("type", "hand_coded")
    old_prod = registry["production"].get(model_type)

    # Promote
    registry["production"][model_type] = filename
    entry["promoted_at"] = datetime.now().isoformat()

    save_registry(registry)

    print("=" * 60)
    print("MODEL PROMOTED TO PRODUCTION")
    print("=" * 60)
    print(f"  Type:     {model_type}")
    print(f"  File:     {filename}")
    print(f"  AUC:      {entry.get('mean_auc', 'N/A')}")
    print(f"  Subjects: {entry.get('n_subjects', 'N/A')}")
    if old_prod:
        print(f"  Previous: {old_prod} (archived, still on disk)")
    else:
        print(f"  Previous: (none — first production model)")
    print()
    print("Restart the API server to load the new model.")
    print(DISCLAIMER)
    return True


def promote_latest(registry, model_type):
    """Promote the latest model of a given type."""
    candidates = [
        e for e in registry["models"]
        if e.get("type") == model_type
    ]
    if not candidates:
        print(f"ERROR: No models of type '{model_type}' found in registry.")
        return False

    latest = max(candidates, key=lambda e: e.get("trained_at", ""))
    return promote(registry, latest["filename"])


def main():
    parser = argparse.ArgumentParser(description="Promote a model to production")
    parser.add_argument("--filename", help="Exact model filename to promote")
    parser.add_argument("--latest", metavar="TYPE",
                        help="Promote latest model of TYPE (hand_coded or cnn)")
    parser.add_argument("--list", action="store_true", help="List all registered models")
    args = parser.parse_args()

    registry = load_registry()

    if args.list:
        list_models(registry)
    elif args.filename:
        promote(registry, args.filename)
    elif args.latest:
        promote_latest(registry, args.latest)
    else:
        # Default: show list
        list_models(registry)
        print("\nUsage:")
        print("  python src/promote_model.py --filename model_B_v1_20260422.pkl")
        print("  python src/promote_model.py --latest hand_coded")
        print("  python src/promote_model.py --list")


if __name__ == "__main__":
    main()
