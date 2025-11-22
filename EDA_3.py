# -*- coding: utf-8 -*-
"""
01 Exploratory Data Analysis (EDA) for Novel Dataset

This script:
- Loads novel_processed.csv from Desktop
- Summarizes dataset structure and missing values
- Computes descriptive statistics for key numeric features
- Generates distribution plots (histograms & boxplots)
- Generates correlation heatmap for key numeric features
- Generates simple scatter plots for important relationships

All outputs (titles, axis labels, file names) are in ENGLISH.
"""

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# ------------------------------------------------------------------
# 1. PATHS
# ------------------------------------------------------------------
DESKTOP = r"C:/Users/18284/Desktop"
INPUT_PATH = os.path.join(DESKTOP, "novel_processed.csv")
OUT_DIR = os.path.join(DESKTOP, "EDA_Novel")
FIG_DIR = os.path.join(OUT_DIR, "figures")
TABLE_DIR = os.path.join(OUT_DIR, "tables")

os.makedirs(FIG_DIR, exist_ok=True)
os.makedirs(TABLE_DIR, exist_ok=True)

# ------------------------------------------------------------------
# 2. MATPLOTLIB GLOBAL STYLE
# ------------------------------------------------------------------
plt.rcParams["font.sans-serif"] = ["Arial"]
plt.rcParams["axes.unicode_minus"] = False
plt.style.use("default")
plt.rcParams.update({
    "figure.autolayout": True,
    "axes.titlesize": 14,
    "axes.labelsize": 11,
    "xtick.labelsize": 9,
    "ytick.labelsize": 9
})

# ------------------------------------------------------------------
# 3. LOAD DATA (WITH ENCODING FALLBACK)
# ------------------------------------------------------------------
def load_data(path: str) -> pd.DataFrame:
    encodings = ["utf-8-sig", "utf-8", "gb18030", "gbk"]
    last_err = None
    for enc in encodings:
        try:
            df_local = pd.read_csv(path, encoding=enc, low_memory=False)
            print(f"✅ Loaded file with encoding: {enc}")
            print(f"   Shape: {df_local.shape[0]} rows × {df_local.shape[1]} columns")
            return df_local
        except Exception as e:
            print(f"[WARN] Failed with encoding {enc}: {e}")
            last_err = e
    raise ValueError(f"❌ Cannot decode CSV with common encodings. Last error: {last_err}")

df = load_data(INPUT_PATH)

# ------------------------------------------------------------------
# 4. ENGLISH NAMES FOR IMPORTANT NUMERIC COLUMNS
#    (Only for display / plots; raw column names are kept as-is)
# ------------------------------------------------------------------
NUM_COL_EN_MAP = {
    "字数": "Word Count",
    "非v章节章均点击数": "Avg Clicks per Non-VIP Chapter",
    "总书评数": "Total Reviews",
    "当前被收藏数": "Current Favorites",
    "文章积分": "Article Score",
    "评分": "Rating",
    "评价人数": "Number of Evaluators",
    "五星比例": "5-Star Ratio",
    "四星比例": "4-Star Ratio",
    "三星比例": "3-Star Ratio"
}

def en_name(col: str) -> str:
    """Return English display name for a column (fallback to raw name)."""
    return NUM_COL_EN_MAP.get(col, col)

def safe_name(col: str) -> str:
    """Generate a safe filename fragment from English display name."""
    s = en_name(col)
    s = s.lower()
    for ch in [" ", "-", "%", "/", "\\", "(", ")", "[", "]", ":"]:
        s = s.replace(ch, "_")
    while "__" in s:
        s = s.replace("__", "_")
    return s.strip("_")

# ------------------------------------------------------------------
# 5. BASIC DATASET SUMMARY
# ------------------------------------------------------------------
report_lines = []

report_lines.append("# Dataset Overview\n")
report_lines.append(f"- Number of rows: {df.shape[0]}\n")
report_lines.append(f"- Number of columns: {df.shape[1]}\n\n")

# Data types summary
dtypes_summary = df.dtypes.astype(str).value_counts()
report_lines.append("## Column Types\n")
for dtype, cnt in dtypes_summary.items():
    report_lines.append(f"- {dtype}: {cnt} columns\n")
report_lines.append("\n")

# Missing values summary
na_count = df.isna().sum()
na_ratio = na_count / len(df)

na_table = pd.DataFrame({
    "column": df.columns,
    "missing_count": na_count.values,
    "missing_ratio": na_ratio.values
}).sort_values("missing_count", ascending=False)

na_table.to_csv(os.path.join(TABLE_DIR, "missing_values_summary.csv"),
                index=False, encoding="utf-8-sig")

report_lines.append("## Missing Values\n")
report_lines.append("- Detailed table saved as: missing_values_summary.csv\n")
report_lines.append("- Located in 'tables' folder.\n\n")

# Save summary report
report_path = os.path.join(OUT_DIR, "EDA_report_basic.txt")
with open(report_path, "w", encoding="utf-8") as f:
    f.write("\n".join(report_lines))
print(f"📝 Saved basic EDA report: {report_path}")

# ------------------------------------------------------------------
# 6. SELECT KEY NUMERIC FEATURES
# ------------------------------------------------------------------
numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()
print(f"Found {len(numeric_cols)} numeric columns in total.")

# Key numeric columns we care about (only keep those that exist)
KEY_NUMERIC_COLS = [
    "字数",
    "总书评数",
    "当前被收藏数",
    "文章积分",
    "评分",
    "评价人数"
]
key_num_cols_present = [c for c in KEY_NUMERIC_COLS if c in numeric_cols]
print("Key numeric columns used for plots:")
for c in key_num_cols_present:
    print(" -", c, "->", en_name(c))

# ------------------------------------------------------------------
# 7. DESCRIPTIVE STATISTICS FOR KEY NUMERIC FEATURES
# ------------------------------------------------------------------
if key_num_cols_present:
    desc = df[key_num_cols_present].describe(
        percentiles=[0.25, 0.5, 0.75, 0.9, 0.95, 0.99]
    ).T
    desc.to_csv(os.path.join(TABLE_DIR, "key_numeric_descriptive_stats.csv"),
                encoding="utf-8-sig")
    print("📊 Saved descriptive statistics for key numeric features.")
else:
    print("[INFO] No key numeric columns found for descriptive statistics.")

# ------------------------------------------------------------------
# 8. HISTOGRAMS FOR KEY NUMERIC FEATURES
# ------------------------------------------------------------------
def plot_histograms(df_local: pd.DataFrame, cols: list):
    for col in cols:
        data = df_local[col].dropna()
        if data.empty:
            print(f"[INFO] Column {col} has no data, skip histogram.")
            continue

        plt.figure(figsize=(6, 4))
        plt.hist(data, bins=40)
        plt.title(f"Distribution of {en_name(col)}")
        plt.xlabel(en_name(col))
        plt.ylabel("Frequency")
        plt.tight_layout()

        fname = f"hist_{safe_name(col)}.png"
        out_path = os.path.join(FIG_DIR, fname)
        plt.savefig(out_path, dpi=300)
        plt.close()
        print(f"📈 Saved histogram: {out_path}")

if key_num_cols_present:
    plot_histograms(df, key_num_cols_present)

# ------------------------------------------------------------------
# 9. BOXPLOTS FOR KEY NUMERIC FEATURES
# ------------------------------------------------------------------
def plot_boxplots(df_local: pd.DataFrame, cols: list):
    # Boxplot of all key numeric columns together (horizontal)
    data = [df_local[c].dropna().values for c in cols]
    labels = [en_name(c) for c in cols]

    plt.figure(figsize=(8, 5))
    plt.boxplot(data, vert=False, labels=labels, showfliers=True)
    plt.title("Boxplot of Key Numeric Features")
    plt.xlabel("Value")
    plt.tight_layout()

    out_path = os.path.join(FIG_DIR, "boxplot_key_numeric.png")
    plt.savefig(out_path, dpi=300)
    plt.close()
    print(f"📦 Saved boxplot: {out_path}")

if key_num_cols_present:
    plot_boxplots(df, key_num_cols_present)

# ------------------------------------------------------------------
# 10. CORRELATION HEATMAP FOR KEY NUMERIC FEATURES
# ------------------------------------------------------------------
def plot_correlation_heatmap(df_local: pd.DataFrame, cols: list):
    corr = df_local[cols].corr()

    plt.figure(figsize=(6, 5))
    im = plt.imshow(corr.values, cmap="viridis", aspect="auto")
    plt.colorbar(im)

    labels = [en_name(c) for c in cols]
    plt.xticks(range(len(cols)), labels, rotation=45, ha="right")
    plt.yticks(range(len(cols)), labels)
    plt.title("Correlation Heatmap of Key Numeric Features")
    plt.tight_layout()

    out_path = os.path.join(FIG_DIR, "corr_heatmap_key_numeric.png")
    plt.savefig(out_path, dpi=300)
    plt.close()
    print(f"🔥 Saved correlation heatmap: {out_path}")

if len(key_num_cols_present) >= 2:
    plot_correlation_heatmap(df, key_num_cols_present)
else:
    print("[INFO] Not enough numeric columns for correlation heatmap.")

# ------------------------------------------------------------------
# 11. SCATTER PLOTS FOR IMPORTANT RELATIONSHIPS
# ------------------------------------------------------------------
SCATTER_PAIRS = [
    ("总书评数", "当前被收藏数"),  # Total Reviews vs Favorites
    ("当前被收藏数", "文章积分"),  # Favorites vs Article Score
    ("字数", "当前被收藏数"),    # Word Count vs Favorites
    ("评分", "文章积分")         # Rating vs Article Score
]

def plot_scatter_pairs(df_local: pd.DataFrame, pairs: list):
    for x_col, y_col in pairs:
        if x_col not in df_local.columns or y_col not in df_local.columns:
            print(f"[INFO] Skip scatter: {x_col} or {y_col} not in columns.")
            continue

        x = df_local[x_col]
        y = df_local[y_col]
        mask = x.notna() & y.notna()
        x = x[mask]
        y = y[mask]

        if x.empty:
            print(f"[INFO] No valid data for scatter {x_col} vs {y_col}, skip.")
            continue

        plt.figure(figsize=(6, 4))
        plt.scatter(x, y, alpha=0.3)
        plt.title(f"Scatter: {en_name(x_col)} vs {en_name(y_col)}")
        plt.xlabel(en_name(x_col))
        plt.ylabel(en_name(y_col))
        plt.tight_layout()

        fname = f"scatter_{safe_name(x_col)}_vs_{safe_name(y_col)}.png"
        out_path = os.path.join(FIG_DIR, fname)
        plt.savefig(out_path, dpi=300)
        plt.close()
        print(f"🔍 Saved scatter plot: {out_path}")

plot_scatter_pairs(df, SCATTER_PAIRS)

print("\n🎯 EDA finished.")
print(f"Figures saved in: {FIG_DIR}")
print(f"Tables saved in : {TABLE_DIR}")
print(f"Basic text report: {report_path}")
