# -*- coding: utf-8 -*-
"""
Visualize TOP 10 one-hot categorical features from novel_processed.csv

Targets (Top 10 each):
- 类型_*   (Genres)
- 视角_*   (Viewpoints)
- 标签_*   (Tags)
- 版权_*   (Copyright types)

All titles / axis labels / category names in FIGURES are in ENGLISH.
"""

import os
import pandas as pd
import matplotlib.pyplot as plt

# ---------- PATHS ----------
DESKTOP = "C:/Users/18284/Desktop"
INPUT_PATH = f"{DESKTOP}/novel_processed.csv"
OUT_DIR = f"{DESKTOP}/Cat_Visual_Top10"
FIG_DIR = os.path.join(OUT_DIR, "figures")
TABLE_DIR = os.path.join(OUT_DIR, "tables")

os.makedirs(FIG_DIR, exist_ok=True)
os.makedirs(TABLE_DIR, exist_ok=True)

# ---------- PLOT STYLE ----------
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

# ---------- LOAD DATA ----------
def load_data(path):
    for enc in ["utf-8-sig", "utf-8", "gb18030", "gbk"]:
        try:
            df = pd.read_csv(path, encoding=enc, low_memory=False)
            print(f"✅ Loaded {path} with encoding {enc}, "
                  f"{df.shape[0]} rows × {df.shape[1]} cols")
            return df
        except UnicodeDecodeError:
            print(f"[WARN] Failed with encoding {enc}, trying next...")
    raise ValueError("❌ Cannot decode CSV file with common encodings.")

df = load_data(INPUT_PATH)

# ---------- MANUAL CN → EN MAPPINGS (only for current TOP 10) ----------

# 1) Genres (类型_*)
GENRE_EN_MAP = {
    "原创": "Original fiction",
    "爱情": "Romance",
    "近代现代": "Contemporary",
    "言情": "Romantic fiction",
    "女主": "Female protagonist",
    "纯爱": "Pure love",
    "架空历史": "Alternate history",
    "主受": "Uke (bottom) MC",
    "衍生": "Derivative / fanfiction",
    "幻想未来": "Futuristic fantasy",
}

# 2) Viewpoints (视角_*)
VIEW_EN_MAP = {
    "女主": "Female POV",
    "主受": "Uke POV",
    "主攻": "Seme POV",
    "男主": "Male POV",
    "不明": "Unknown POV",
    "双视角": "Dual POV",
    "互攻": "Switch POV",
    "未知": "Unknown POV",
    "其他": "Other POV",
    "多视角": "Multiple POVs",
}

# 3) Copyright types (版权_*)
COPYRIGHT_EN_MAP = {
    "中国大陆出版最新签约": "Mainland China publishing (latest)",
    "无匹配结果": "No match",
    "繁体出版_港_台_签约": "Traditional Chinese HK/TW publishing",
    "广播剧签约": "Audio drama contract",
    "网络剧签约": "Web series contract",
    "亚洲出版签约": "Asia publishing contract",
    "电视剧签约": "TV series contract",
    "有声读物签约": "Audiobook contract",
    "衍生品签约": "Merchandise contract",
    "港澳出版签约": "HK/Macau publishing contract",
}

# 4) Tags (标签_*)
TAG_EN_MAP = {
    "轻松": "Light-hearted",
    "甜文": "Sweet",
    "情有独钟": "Devoted love",
    "正剧": "Serious plot",
    "都市": "Urban",
    "爽文": "Power fantasy",
    "天作之合": "Perfect match",
    "成长": "Coming-of-age",
    "强强": "Strong x strong",
    "穿越时空": "Time travel",
}


# ---------- HELPER: TOP10 PLOT ----------
def plot_top10_onehot(df, prefix, title, fig_filename, table_filename, mapping=None):
    """
    Take one-hot columns with given prefix, compute Top 10,
    optionally map CN category names to EN with `mapping`.
    """
    cols = [c for c in df.columns if c.startswith(prefix)]
    if not cols:
        print(f"[INFO] No columns starting with '{prefix}', skip.")
        return

    counts = df[cols].sum().sort_values(ascending=False).head(10)

    # raw Chinese suffixes
    categories_raw = [c.replace(prefix, "") for c in counts.index]

    # apply mapping (if provided) to get English labels
    if mapping is not None:
        categories_en = [mapping.get(cn, cn) for cn in categories_raw]
    else:
        categories_en = categories_raw

    # save table (English category names)
    out_table_path = os.path.join(TABLE_DIR, table_filename)
    pd.DataFrame({
        "Category_EN": categories_en,
        "Category_raw": categories_raw,
        "Count": counts.values
    }).to_csv(out_table_path, index=False, encoding="utf-8-sig")
    print(f"📄 Saved top10 table: {out_table_path}")

    # plot
    plt.figure(figsize=(9, 4))
    plt.bar(categories_en, counts.values)
    plt.title(title)
    plt.xlabel("Category")
    plt.ylabel("Count")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    out_fig_path = os.path.join(FIG_DIR, fig_filename)
    plt.savefig(out_fig_path, dpi=300)
    plt.close()
    print(f"📊 Saved figure: {out_fig_path}")


# ---------- PLOTS FOR EACH CATEGORY ----------

# Genres
plot_top10_onehot(
    df,
    prefix="类型_",
    title="Top 10 Genres",
    fig_filename="top10_genres.png",
    table_filename="top10_genres.csv",
    mapping=GENRE_EN_MAP
)

# Viewpoints
plot_top10_onehot(
    df,
    prefix="视角_",
    title="Top 10 Viewpoints",
    fig_filename="top10_viewpoints.png",
    table_filename="top10_viewpoints.csv",
    mapping=VIEW_EN_MAP
)

# Tags
plot_top10_onehot(
    df,
    prefix="标签_",
    title="Top 10 Tags",
    fig_filename="top10_tags.png",
    table_filename="top10_tags.csv",
    mapping=TAG_EN_MAP
)

# Copyright types
plot_top10_onehot(
    df,
    prefix="版权_",
    title="Top 10 Copyright Types",
    fig_filename="top10_copyright.png",
    table_filename="top10_copyright.csv",
    mapping=COPYRIGHT_EN_MAP
)

print("\n🎯 All Top-10 visualizations finished.")
print(f"Figures saved in: {FIG_DIR}")
print(f"Tables saved in : {TABLE_DIR}")
