"""
EDA Report — Positive-Only Analysis
Generates reports/eda_positive_only.pdf with:
  - Feature distributions across 15 subjects
  - Within-subject variance (between frames of the same woman)
  - Between-subject variance
  - Per-subject boxplots for each feature
  - Variance ratio analysis (between/within)

No models, no predictions, no probability scores.
Research use only. Experimental probability model. Not a diagnostic test.
"""

import os
import sys
from datetime import datetime

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import seaborn as sns

# Paths
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FEATURES_CSV = os.path.join(PROJECT_ROOT, "data", "processed", "features.csv")
REPORTS_DIR = os.path.join(PROJECT_ROOT, "reports")
PDF_PATH = os.path.join(REPORTS_DIR, "eda_positive_only.pdf")

FEATURE_NAMES = [
    "r_mean", "g_mean", "b_mean", "brightness", "turbidity",
    "dominant_hue", "hue_spread", "texture_score", "edge_intensity",
    "bubble_count", "contrast", "saturation", "color_variance",
    "yellowness", "gy_ratio",
]

sns.set_theme(style="whitegrid", font_scale=0.9)
PALETTE = sns.color_palette("tab20", 15)


def compute_variance_decomposition(df, feature_cols):
    """
    Decompose total variance into within-subject and between-subject.
    Returns a DataFrame with one row per feature.
    """
    rows = []
    for feat in feature_cols:
        if feat not in df.columns:
            continue

        grand_mean = df[feat].mean()
        total_var = df[feat].var()

        # Within-subject variance: average of per-subject variances
        per_subject = df.groupby("subject_id")[feat]
        within_vars = per_subject.var().dropna()
        within_var = within_vars.mean() if len(within_vars) > 0 else 0.0

        # Between-subject variance: variance of subject means
        subject_means = per_subject.mean()
        between_var = subject_means.var() if len(subject_means) > 1 else 0.0

        # ICC-like ratio: between / (between + within)
        total = between_var + within_var
        icc = between_var / total if total > 0 else 0.0

        rows.append({
            "feature": feat,
            "grand_mean": round(grand_mean, 4),
            "total_var": round(total_var, 4),
            "within_subject_var": round(within_var, 4),
            "between_subject_var": round(between_var, 4),
            "icc_ratio": round(icc, 4),
        })

    return pd.DataFrame(rows)


def generate_pdf(df):
    """Generate the full EDA PDF report."""
    os.makedirs(REPORTS_DIR, exist_ok=True)

    feature_cols = [f for f in FEATURE_NAMES if f in df.columns]
    subjects = sorted(df["subject_id"].unique(), key=lambda x: int(x.split("_")[1]) if "_" in x and x.split("_")[1].isdigit() else x)
    n_subjects = len(subjects)

    # Variance decomposition
    var_df = compute_variance_decomposition(df, feature_cols)

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with PdfPages(PDF_PATH) as pdf:

        # ============================================================
        # PAGE 1: Title + Dataset Summary
        # ============================================================
        fig, ax = plt.subplots(figsize=(11, 8.5))
        ax.axis("off")

        title_text = "Pregnancy Detection AI\nEDA Report — Positive Samples Only"
        ax.text(0.5, 0.85, title_text, transform=ax.transAxes,
                fontsize=22, fontweight="bold", ha="center", va="top")

        n_photos = len(df[df["media_type"] == "photo"])
        n_vframes = len(df[df["media_type"] == "video_frame"])

        summary = (
            f"Generated: {timestamp}\n\n"
            f"Subjects: {n_subjects}\n"
            f"Total images: {len(df)}  (photos: {n_photos}, video frames: {n_vframes})\n"
            f"Features extracted: {len(feature_cols)}\n"
            f"Images per subject: {len(df) / n_subjects:.1f} (avg)\n\n"
            f"Label: ALL samples are label=1 (pregnant / positive)\n"
            f"No NEGATIVE samples available yet.\n"
            f"No models trained. No probability scores generated.\n\n"
            f"Research use only. Experimental probability model. Not a diagnostic test."
        )
        ax.text(0.5, 0.55, summary, transform=ax.transAxes,
                fontsize=12, ha="center", va="top", family="monospace")

        pdf.savefig(fig)
        plt.close()

        # ============================================================
        # PAGE 2: Variance Decomposition Table
        # ============================================================
        fig, ax = plt.subplots(figsize=(11, 8.5))
        ax.axis("off")
        ax.set_title("Variance Decomposition: Within-Subject vs Between-Subject",
                      fontsize=14, fontweight="bold", pad=20)

        # Render table
        table_data = []
        for _, row in var_df.iterrows():
            table_data.append([
                row["feature"],
                f"{row['grand_mean']:.2f}",
                f"{row['within_subject_var']:.2f}",
                f"{row['between_subject_var']:.2f}",
                f"{row['icc_ratio']:.3f}",
            ])

        col_labels = ["Feature", "Grand Mean", "Within-Subj Var", "Between-Subj Var", "ICC Ratio"]
        table = ax.table(
            cellText=table_data,
            colLabels=col_labels,
            loc="center",
            cellLoc="center",
        )
        table.auto_set_font_size(False)
        table.set_fontsize(9)
        table.scale(1.0, 1.6)

        # Color header
        for j in range(len(col_labels)):
            table[0, j].set_facecolor("#2c3e50")
            table[0, j].set_text_props(color="white", fontweight="bold")

        # Highlight high ICC rows (strong between-subject signal)
        for i, row in enumerate(var_df.itertuples(), start=1):
            if row.icc_ratio > 0.5:
                for j in range(len(col_labels)):
                    table[i, j].set_facecolor("#d5f4e6")

        ax.text(0.5, 0.08,
                "ICC Ratio > 0.5 (highlighted green) = feature varies MORE between subjects than within.\n"
                "These features are most stable per-person and differ most person-to-person.",
                transform=ax.transAxes, fontsize=9, ha="center", style="italic")

        pdf.savefig(fig)
        plt.close()

        # ============================================================
        # PAGE 3: ICC Bar Chart
        # ============================================================
        fig, ax = plt.subplots(figsize=(11, 6))
        sorted_var = var_df.sort_values("icc_ratio", ascending=True)
        colors = ["#27ae60" if v > 0.5 else "#e74c3c" if v < 0.2 else "#f39c12"
                  for v in sorted_var["icc_ratio"]]
        ax.barh(sorted_var["feature"], sorted_var["icc_ratio"], color=colors)
        ax.axvline(x=0.5, color="gray", linestyle="--", alpha=0.7, label="ICC=0.5 threshold")
        ax.set_xlabel("ICC Ratio (Between / Total Variance)")
        ax.set_title("Feature Stability: Between-Subject vs Within-Subject Variance",
                      fontweight="bold")
        ax.legend()
        ax.set_xlim(0, 1)
        plt.tight_layout()
        pdf.savefig(fig)
        plt.close()

        # ============================================================
        # PAGES 4+: Per-feature boxplots by subject
        # ============================================================
        # 3 features per page
        for page_start in range(0, len(feature_cols), 3):
            page_feats = feature_cols[page_start:page_start + 3]
            n_plots = len(page_feats)

            fig, axes = plt.subplots(n_plots, 1, figsize=(11, 3.5 * n_plots))
            if n_plots == 1:
                axes = [axes]

            for ax, feat in zip(axes, page_feats):
                # Sort subjects by numeric ID
                order = subjects
                sns.boxplot(
                    data=df, x="subject_id", y=feat, hue="subject_id",
                    order=order, hue_order=order,
                    palette=PALETTE[:n_subjects], ax=ax, fliersize=3,
                    legend=False,
                )
                ax.set_title(f"{feat} — Distribution per Subject", fontweight="bold")
                ax.set_xlabel("")
                ax.tick_params(axis="x", rotation=45)

                # Add subject sample count
                counts = df.groupby("subject_id").size()
                for i, subj in enumerate(order):
                    n = counts.get(subj, 0)
                    ax.text(i, ax.get_ylim()[1], f"n={n}", ha="center", va="bottom", fontsize=7)

            plt.tight_layout()
            pdf.savefig(fig)
            plt.close()

        # ============================================================
        # Feature Histograms — all subjects overlaid
        # ============================================================
        n_cols = 3
        n_rows = (len(feature_cols) + n_cols - 1) // n_cols
        fig, axes = plt.subplots(n_rows, n_cols, figsize=(11, 3 * n_rows))
        axes = axes.flatten()

        for i, feat in enumerate(feature_cols):
            ax = axes[i]
            ax.hist(df[feat].dropna(), bins=30, color="#3498db", alpha=0.7, edgecolor="white")
            ax.set_title(feat, fontweight="bold", fontsize=10)
            ax.axvline(df[feat].mean(), color="red", linestyle="--", linewidth=1, label="mean")
            ax.legend(fontsize=7)

        for j in range(i + 1, len(axes)):
            axes[j].set_visible(False)

        plt.suptitle("Feature Histograms (All Positive Samples Pooled)", fontsize=14, fontweight="bold")
        plt.tight_layout()
        pdf.savefig(fig)
        plt.close()

        # ============================================================
        # Correlation Matrix
        # ============================================================
        fig, ax = plt.subplots(figsize=(11, 9))
        corr = df[feature_cols].corr()
        mask = np.triu(np.ones_like(corr, dtype=bool), k=1)
        sns.heatmap(corr, mask=mask, annot=True, fmt=".2f", cmap="RdBu_r",
                    center=0, square=True, ax=ax, vmin=-1, vmax=1,
                    annot_kws={"size": 7})
        ax.set_title("Feature Correlation Matrix (Positive Samples)", fontweight="bold")
        plt.tight_layout()
        pdf.savefig(fig)
        plt.close()

        # ============================================================
        # Per-subject mean heatmap
        # ============================================================
        subject_means = df.groupby("subject_id")[feature_cols].mean()
        # Sort by subject number
        subject_means = subject_means.reindex(subjects)

        # Standardize for visualization
        from sklearn.preprocessing import StandardScaler
        scaler = StandardScaler()
        scaled = pd.DataFrame(
            scaler.fit_transform(subject_means),
            index=subject_means.index,
            columns=subject_means.columns,
        )

        fig, ax = plt.subplots(figsize=(11, 7))
        sns.heatmap(scaled.T, cmap="RdYlGn", center=0, annot=True, fmt=".1f",
                    ax=ax, annot_kws={"size": 7}, linewidths=0.5)
        ax.set_title("Subject Feature Profiles (Z-scored)\nEach column = one woman's average features",
                      fontweight="bold")
        ax.set_xlabel("Subject")
        ax.set_ylabel("Feature")
        plt.tight_layout()
        pdf.savefig(fig)
        plt.close()

        # ============================================================
        # Within-subject CV (coefficient of variation) per feature
        # ============================================================
        fig, ax = plt.subplots(figsize=(11, 6))

        cv_data = []
        for feat in feature_cols:
            for subj in subjects:
                subj_data = df[df["subject_id"] == subj][feat]
                if len(subj_data) > 1 and subj_data.mean() != 0:
                    cv = subj_data.std() / abs(subj_data.mean())
                    cv_data.append({"feature": feat, "subject_id": subj, "cv": cv})

        if cv_data:
            cv_df = pd.DataFrame(cv_data)
            sns.boxplot(data=cv_df, x="feature", y="cv", color="#9b59b6", ax=ax, fliersize=2)
            ax.set_title("Within-Subject Coefficient of Variation (CV)\nLower = more consistent across frames",
                          fontweight="bold")
            ax.set_ylabel("CV (std/mean)")
            ax.tick_params(axis="x", rotation=45)
            ax.axhline(y=0.1, color="green", linestyle="--", alpha=0.5, label="CV=0.1 (stable)")
            ax.legend()
        plt.tight_layout()
        pdf.savefig(fig)
        plt.close()

    print(f"\nEDA report saved: {PDF_PATH}")
    print(f"Research use only. Experimental probability model. Not a diagnostic test.")
    return PDF_PATH


def run_eda():
    if not os.path.exists(FEATURES_CSV):
        print(f"ERROR: {FEATURES_CSV} not found. Run build_index.py and phase1_extract.py first.")
        sys.exit(1)

    df = pd.read_csv(FEATURES_CSV)
    print(f"Loaded features: {df.shape}")
    print(f"Subjects: {df['subject_id'].nunique()}")

    return generate_pdf(df)


if __name__ == "__main__":
    run_eda()
