"""
Non-regular Employment Structure: Japan vs. Sweden (2024)
============================================================
Part B of the labor-market portfolio project. Python rebuild of
Sophie's original coursework scripts (nonregular.R and
part_time_sweden.R, originally in R) — the original code was found,
so this is a faithful Python re-implementation with cleaner,
publication-style charts.

What it does:
  1. Japan: reads the e-Stat Labour Force Survey CSV
     (Table 1-2-4, cached under data/), keeps 2024 / all industries /
     Male+Female, and computes the non-regular share of employees
     (Non-regular staff / Employees excl. executives) for six age
     groups.
  2. Sweden: uses the 2024 quarterly-average temporary-employment
     shares compiled from Eurostat (hand-compiled in the original
     coursework; see part_time_sweden.R).
  3. Produces three charts under figures/ and prints the key
     numerical findings to the console.

Run:  python analysis_nonregular.py   (from this directory)

Note on comparability: Japan's "non-regular" and Sweden's "temporary"
follow different national definitions, so cross-country levels are
not strictly comparable — each is best read within its own
definition. The comparison chart (fig7) is limited to the one age
band (15-24) measured identically in both datasets.
"""

import os

import matplotlib

matplotlib.use("Agg")  # headless: no display needed
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
import pandas as pd
import seaborn as sns

# ---------------------------------------------------------------- locations
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
FIG_DIR = os.path.join(BASE_DIR, "figures")
os.makedirs(FIG_DIR, exist_ok=True)

ESTAT_CSV = os.path.join(DATA_DIR, "estat_nonregular_jpn.csv")
JPN_TIDY_CSV = os.path.join(DATA_DIR, "jpn_nonregular_2024_tidy.csv")

# ---------------------------------------------------------------- constants
JP_RED = "#BC002D"      # Japan accent (matches Part A)
SE_BLUE = "#006AA7"     # Sweden accent (matches Part A)
FEMALE = "#C0392B"      # female bars
MALE = "#2E6E8E"        # male bars

# Six age bands used in the original R script (e-Stat column names)
AGE_COLS = [
    "15 to 24 years old",
    "25 to 34 years old",
    "35 to 44 years old",
    "45 to 54 years old",
    "55 to 64 years old",
    "65 years old or more",
]
AGE_LABELS = ["15–24", "25–34", "35–44", "45–54", "55–64", "65+"]

DENOM = "Employee, excl. executive of company or corporation"
NUMER = "Non-regular staff"

# Sweden: 2024 quarterly averages of temporary employees as % of all
# employees, compiled from Eurostat (see original part_time_sweden.R)
SWEDEN_TEMP = pd.DataFrame(
    {
        "age_group": ["15–24", "25–49", "50–59"],
        "Female": [55.95, 10.30, 5.28],
        "Male": [45.30, 8.95, 3.55],
    }
)

sns.set_theme(style="whitegrid", rc={
    "figure.dpi": 150, "axes.titlesize": 13, "axes.titleweight": "bold",
    "axes.labelsize": 11, "xtick.labelsize": 10, "ytick.labelsize": 10,
    "legend.fontsize": 10,
})


# ------------------------------------------------------------------ helpers
def _source_caption(ax, text):
    """Small source note at the bottom-left of a chart."""
    ax.text(
        0, -0.14, text, transform=ax.transAxes, ha="left", va="top",
        fontsize=8, color="#666666",
    )


def _pct_axis(ax):
    ax.xaxis.set_major_formatter(mticker.PercentFormatter(xmax=1.0))


# ------------------------------------------------------------------- Japan
def load_japan():
    """Read the e-Stat CSV and compute non-regular shares (2024)."""
    raw = pd.read_csv(ESTAT_CSV, skiprows=13, encoding="cp932")

    df = raw[
        (raw["Time (Yearly)"].astype(int) == 2024)
        & (raw["Industry"] == "All industries")
        & (raw["Sex"].isin(["Male", "Female"]))
        & (raw["Type of employment"].isin([DENOM, NUMER]))
    ][["Sex", "Type of employment"] + AGE_COLS].copy()

    # Wide: one row per sex, one column per (age band x employment type)
    long = df.melt(
        id_vars=["Sex", "Type of employment"],
        value_vars=AGE_COLS,
        var_name="age_group",
        value_name="n_10k",
    )
    wide = long.pivot_table(
        index=["Sex", "age_group"], columns="Type of employment",
        values="n_10k", aggfunc="first",
    ).reset_index()
    wide["share"] = wide[NUMER] / wide[DENOM]
    wide["age_label"] = pd.Categorical(
        wide["age_group"].map(dict(zip(AGE_COLS, AGE_LABELS))),
        categories=AGE_LABELS, ordered=True,
    )
    wide = wide.sort_values(["Sex", "age_label"]).reset_index(drop=True)
    return wide[["Sex", "age_label", "share"]]


def chart_japan(df):
    """fig5: grouped horizontal bars — Japan non-regular share by age & sex."""
    fig, ax = plt.subplots(figsize=(9, 5.2))
    y = np.arange(len(AGE_LABELS))
    h = 0.36
    for i, (sex, color) in enumerate([("Female", FEMALE), ("Male", MALE)]):
        vals = df[df["Sex"] == sex].set_index("age_label").loc[AGE_LABELS, "share"]
        bars = ax.barh(y + (i - 0.5) * h, vals.values, height=h,
                       color=color, label=sex)
        # annotate the two most policy-relevant bars lightly
        for yy, v in zip(y + (i - 0.5) * h, vals.values):
            ax.text(v + 0.008, yy, f"{v:.0%}", va="center", fontsize=8.5,
                    color="#333333")
    ax.set_yticks(y)
    ax.set_yticklabels(AGE_LABELS)
    ax.invert_yaxis()
    ax.set_xlabel("Non-regular staff (% of employees excl. executives)")
    ax.set_title("Non-regular employment in Japan by age group and sex, 2024")
    _pct_axis(ax)
    ax.set_xlim(0, 0.97)
    ax.legend(frameon=True, loc="upper left")
    _source_caption(ax, "Source: e-Stat, Labour Force Survey, Table 1-2-4 (2024).")
    fig.tight_layout()
    fig.savefig(os.path.join(FIG_DIR, "fig5_japan_nonregular_by_age_sex.png"),
                bbox_inches="tight")
    plt.close(fig)


# ------------------------------------------------------------------ Sweden
def chart_sweden():
    """fig6: grouped horizontal bars — Sweden temporary share by age & sex."""
    df = SWEDEN_TEMP.melt(id_vars="age_group", var_name="Sex",
                          value_name="temp_share")
    df["temp_share"] /= 100.0
    order = ["15–24", "25–49", "50–59"]
    fig, ax = plt.subplots(figsize=(9, 4.2))
    y = np.arange(len(order))
    h = 0.36
    for i, (sex, color) in enumerate([("Female", FEMALE), ("Male", MALE)]):
        vals = (df[df["Sex"] == sex].set_index("age_group")
                .loc[order, "temp_share"])
        ax.barh(y + (i - 0.5) * h, vals.values, height=h,
                color=color, label=sex)
        for yy, v in zip(y + (i - 0.5) * h, vals.values):
            ax.text(v + 0.008, yy, f"{v:.1%}", va="center", fontsize=8.5,
                    color="#333333")
    ax.set_yticks(y)
    ax.set_yticklabels(order)
    ax.invert_yaxis()
    ax.set_xlabel("Temporary employees (% of all employees, 2024 average)")
    ax.set_title("Temporary employment in Sweden by age group and sex, 2024")
    _pct_axis(ax)
    ax.set_xlim(0, 0.68)
    ax.legend(frameon=True, loc="lower right")
    _source_caption(
        ax,
        "Source: Eurostat quarterly data, compiled as 2024 average "
        "(from original coursework).",
    )
    fig.tight_layout()
    fig.savefig(os.path.join(FIG_DIR, "fig6_sweden_temporary_by_age_sex.png"),
                bbox_inches="tight")
    plt.close(fig)


# --------------------------------------------------------------- comparison
def chart_youth_comparison(jpn):
    """fig7: 15-24 non-regular/temporary share, Japan vs Sweden by sex.

    15-24 is the only age band measured identically in both datasets,
    so the comparison is restricted to it.
    """
    jpn_youth = (jpn[jpn["age_label"] == "15–24"]
                 .set_index("Sex")["share"])
    rows = [
        ("Japan", "Female", jpn_youth["Female"], JP_RED),
        ("Japan", "Male", jpn_youth["Male"], JP_RED),
        ("Sweden", "Female", 0.5595, SE_BLUE),
        ("Sweden", "Male", 0.4530, SE_BLUE),
    ]
    labels = [f"{c} · {s}" for c, s, _, _ in rows]
    vals = [v for _, _, v, _ in rows]
    colors = [col for _, _, _, col in rows]

    fig, ax = plt.subplots(figsize=(7.5, 4.4))
    bars = ax.barh(labels, vals, color=colors, height=0.55)
    # hatch male bars so sex is distinguishable beyond the label
    bars[1].set_hatch("///")
    bars[3].set_hatch("///")
    for lab, v in zip(labels, vals):
        ax.text(v + 0.008, lab, f"{v:.1%}", va="center", fontsize=10,
                color="#333333")
    ax.set_xlabel("Non-regular / temporary share of employees (%)")
    ax.set_title("Young workers (15–24) in non-regular / temporary jobs, 2024")
    _pct_axis(ax)
    ax.set_xlim(0, max(vals) * 1.22)
    ax.invert_yaxis()
    fig.subplots_adjust(bottom=0.28)
    fig.text(
        0.01, 0.02,
        "Sources: Japan — e-Stat LFS Table 1-2-4 (non-regular staff, excl. executives);\n"
        "Sweden — Eurostat quarterly average (temporary employees). "
        "Definitions differ; compare levels with care. Hatched = male.",
        ha="left", va="bottom", fontsize=8, color="#666666",
    )
    fig.savefig(os.path.join(FIG_DIR, "fig7_youth_nonregular_comparison.png"),
                bbox_inches="tight")
    plt.close(fig)


# --------------------------------------------------------------------- main
def main():
    jpn = load_japan()
    assert not jpn["share"].isna().any(), "missing shares in Japan data"
    assert len(jpn) == 12, f"expected 12 rows (6 ages x 2 sexes), got {len(jpn)}"

    # tidy cache for transparency / reuse
    jpn.to_csv(JPN_TIDY_CSV, index=False)

    chart_japan(jpn)
    chart_sweden()
    chart_youth_comparison(jpn)

    # ---- console summary (key numbers for README / resume) ----
    piv = jpn.pivot(index="age_label", columns="Sex", values="share")
    print("Japan non-regular share by age group and sex, 2024:")
    print((piv * 100).round(1).to_string())
    print()
    f65, m65 = piv.loc["65+", "Female"], piv.loc["65+", "Male"]
    print(f"Japan 65+: female {f65:.1%}, male {m65:.1%} "
          f"(gap {f65 - m65:.1%})")
    f1524, m1524 = piv.loc["15–24", "Female"], piv.loc["15–24", "Male"]
    print(f"Japan 15-24: female {f1524:.1%}, male {m1524:.1%}")
    print("Sweden temporary 15-24: female 55.9%, male 45.3%")
    print(f"Youth (15-24) Japan vs Sweden — "
          f"female {f1524:.1%} vs 55.9%, male {m1524:.1%} vs 45.3%")
    print()
    print("Wrote: fig5_japan_nonregular_by_age_sex.png, "
          "fig6_sweden_temporary_by_age_sex.png, "
          "fig7_youth_nonregular_comparison.png")


if __name__ == "__main__":
    main()
