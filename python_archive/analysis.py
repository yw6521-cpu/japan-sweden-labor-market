"""
Female Labor Force Participation: Japan vs. Sweden (1990-2025)
================================================================
Rebuild of a coursework project (originally in R) as a Python
portfolio piece for data-analyst job applications.

What it does:
  1. Fetches labor-force participation data from two public APIs:
     - World Bank API: headline participation rates (15+), 1990-2025
     - ILOSTAT SDMX API: participation by 5-year age band, 1990-2024
  2. Caches raw API responses under data/ (falls back to the cache
     if the APIs are unreachable, so the script always runs).
  3. Produces four publication-style charts under figures/ and
     prints the key numerical findings to the console.

Run:  python analysis.py   (from this directory)
"""

import os

import matplotlib

matplotlib.use("Agg")  # headless: no display needed
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import requests
import seaborn as sns

# ---------------------------------------------------------------- locations
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
FIG_DIR = os.path.join(BASE_DIR, "figures")
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(FIG_DIR, exist_ok=True)

WB_CACHE = os.path.join(DATA_DIR, "wb_lfpr_jpn_swe.csv")
ILO_CACHE = os.path.join(DATA_DIR, "ilostat_age_lfpr_jpn_swe.csv")

# ---------------------------------------------------------------- constants
COUNTRIES = {"JPN": "Japan", "SWE": "Sweden"}
JP_RED = "#BC002D"     # Japan
SE_BLUE = "#006AA7"    # Sweden

AGE_CODES = [
    "AGE_5YRBANDS_Y15-19", "AGE_5YRBANDS_Y20-24", "AGE_5YRBANDS_Y25-29",
    "AGE_5YRBANDS_Y30-34", "AGE_5YRBANDS_Y35-39", "AGE_5YRBANDS_Y40-44",
    "AGE_5YRBANDS_Y45-49", "AGE_5YRBANDS_Y50-54", "AGE_5YRBANDS_Y55-59",
    "AGE_5YRBANDS_Y60-64",
]
AGE_LABELS = ["15-19", "20-24", "25-29", "30-34", "35-39",
              "40-44", "45-49", "50-54", "55-59", "60-64"]

sns.set_theme(style="whitegrid", rc={
    "figure.dpi": 150, "axes.titlesize": 14, "axes.titleweight": "bold",
    "axes.labelsize": 11, "xtick.labelsize": 10, "ytick.labelsize": 10,
    "legend.fontsize": 10,
})


# ================================================================ data fetch
def fetch_world_bank() -> pd.DataFrame:
    """Headline LFPR (ages 15+) for Japan & Sweden, 1990-2025, via World Bank API."""
    indicators = {"female": "SL.TLF.CACT.FE.ZS", "male": "SL.TLF.CACT.MA.ZS"}
    frames = []
    for sex, code in indicators.items():
        url = f"https://api.worldbank.org/v2/country/JPN;SWE/indicator/{code}"
        resp = requests.get(url, params={"date": "1990:2025", "format": "json",
                                          "per_page": 300}, timeout=60)
        resp.raise_for_status()
        rows = [
            {"country": r["country"]["value"], "iso": r["countryiso3code"],
             "year": int(r["date"]), "value": r["value"], "sex": sex}
            for r in resp.json()[1] if r["value"] is not None
        ]
        frames.append(pd.DataFrame(rows))
    df = pd.concat(frames, ignore_index=True).sort_values(["iso", "sex", "year"])
    df.to_csv(WB_CACHE, index=False)
    return df


def fetch_ilostat() -> pd.DataFrame:
    """LFPR by 5-year age band, Japan & Sweden, 1990-2024, via ILOSTAT SDMX API."""
    url = ("https://sdmx.ilo.org/rest/v2/data/"
           "ILO,DF_EAP_DWAP_SEX_AGE_RT,1.0/JPN+SWE.A..SEX_F+SEX_M.")
    resp = requests.get(url, params={"startPeriod": "1990", "endPeriod": "2024"},
                        headers={"Accept": "text/csv"}, timeout=120)
    resp.raise_for_status()
    df = pd.read_csv(pd.io.common.BytesIO(resp.content))
    df = df[df["AGE"].isin(AGE_CODES)].copy()
    df["age"] = pd.Categorical(df["AGE"].map(dict(zip(AGE_CODES, AGE_LABELS))),
                               categories=AGE_LABELS, ordered=True)
    df["country"] = df["REF_AREA"].map(COUNTRIES)
    df["sex"] = df["SEX"].map({"SEX_F": "female", "SEX_M": "male"})
    df = df.rename(columns={"REF_AREA": "iso", "TIME_PERIOD": "year",
                             "OBS_VALUE": "value"})
    df = df[["country", "iso", "year", "sex", "age", "value"]]
    df.to_csv(ILO_CACHE, index=False)
    return df


def load_data():
    """Fetch live; fall back to the cached CSVs if the network/APIs fail."""
    try:
        wb = fetch_world_bank()
        print(f"[ok] World Bank API: {len(wb)} rows")
    except Exception as exc:  # noqa: BLE001
        print(f"[warn] World Bank API failed ({exc}); using cached data")
        wb = pd.read_csv(WB_CACHE)
    try:
        ilo = fetch_ilostat()
        print(f"[ok] ILOSTAT API: {len(ilo)} rows")
    except Exception as exc:  # noqa: BLE001
        print(f"[warn] ILOSTAT API failed ({exc}); using cached data")
        ilo = pd.read_csv(ILO_CACHE)
        ilo["age"] = pd.Categorical(ilo["age"], categories=AGE_LABELS, ordered=True)
    return wb, ilo


# =================================================================== figures
def fig1_trend(wb: pd.DataFrame):
    """Long-run female participation trends, Japan vs Sweden."""
    f = wb[wb["sex"] == "female"].pivot(index="year", columns="country", values="value")
    _, ax = plt.subplots(figsize=(10, 5.5))
    ax.plot(f.index, f["Japan"], color=JP_RED, lw=2.5, label="Japan")
    ax.plot(f.index, f["Sweden"], color=SE_BLUE, lw=2.5, label="Sweden")
    for c, col in [("Japan", JP_RED), ("Sweden", SE_BLUE)]:
        y = f[c].dropna()
        ax.annotate(f"{y.iloc[-1]:.1f}%", (y.index[-1], y.iloc[-1]),
                    textcoords="offset points", xytext=(8, 0), color=col,
                    fontweight="bold", fontsize=11)
    ax.set_title("Female labor force participation rate (ages 15+), 1990-2025")
    ax.set_xlabel("Year")
    ax.set_ylabel("% of female population ages 15+")
    ax.set_xlim(f.index.min(), f.index.max() + 1)
    ax.legend(frameon=True, loc="upper left")
    sns.despine()
    plt.tight_layout()
    plt.savefig(os.path.join(FIG_DIR, "fig1_female_lfpr_trend.png"))
    plt.close()


def fig2_age_profile(ilo: pd.DataFrame, year: int = 2024):
    """The 'M-curve': female participation by age, Japan vs Sweden."""
    sub = ilo[(ilo["sex"] == "female") & (ilo["year"] == year)]
    sub = sub.sort_values("age")
    _, ax = plt.subplots(figsize=(10, 5.5))
    for country, color in [("Japan", JP_RED), ("Sweden", SE_BLUE)]:
        s = sub[sub["country"] == country]
        ax.plot(s["age"].astype(str), s["value"], marker="o",
                color=color, lw=2.5, label=country)
    # highlight Japan's mid-career dip
    jp = sub[sub["country"] == "Japan"].set_index("age")["value"]
    dip = jp["25-29"] - jp["30-34"]
    ax.annotate(f"Japan's M-dip: {dip:.1f} pp drop\nat ages 30-34",
                xy=("30-34", jp["30-34"]), xytext=(15, -45),
                textcoords="offset points", fontsize=10,
                arrowprops=dict(arrowstyle="->", color="black"),
                bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="gray"))
    ax.set_title(f"Female participation by age group, {year}\n"
                 "Japan's M-curve vs Sweden's continuous profile")
    ax.set_xlabel("Age group")
    ax.set_ylabel("% of female population in age group")
    ax.legend(frameon=True)
    sns.despine()
    plt.tight_layout()
    plt.savefig(os.path.join(FIG_DIR, "fig2_age_profile_mcurve.png"))
    plt.close()


def fig3_gender_gap(wb: pd.DataFrame):
    """How the male-female participation gap evolved."""
    p = wb.pivot_table(index=["iso", "country", "year"], columns="sex",
                       values="value").reset_index()
    p["gap"] = p["male"] - p["female"]
    _, ax = plt.subplots(figsize=(10, 5.5))
    for country, color in [("Japan", JP_RED), ("Sweden", SE_BLUE)]:
        s = p[p["country"] == country].sort_values("year")
        ax.plot(s["year"], s["gap"], color=color, lw=2.5, label=country)
        ax.annotate(f"{s['gap'].iloc[-1]:.1f} pp", (s["year"].iloc[-1], s["gap"].iloc[-1]),
                    textcoords="offset points", xytext=(8, 0), color=color,
                    fontweight="bold", fontsize=11)
    ax.axhline(0, color="gray", ls="--", lw=1)
    ax.set_title("Gender gap in labor force participation (male minus female), 1990-2025")
    ax.set_xlabel("Year")
    ax.set_ylabel("Percentage points")
    ax.legend(frameon=True, loc="upper right", title="Country")
    sns.despine()
    plt.tight_layout()
    plt.savefig(os.path.join(FIG_DIR, "fig3_gender_gap.png"))
    plt.close()


def fig4_japan_evolution(ilo: pd.DataFrame):
    """Japan's M-curve flattening over three decades."""
    years = [1990, 2000, 2010, 2024]
    sub = ilo[(ilo["country"] == "Japan") & (ilo["sex"] == "female")
              & (ilo["year"].isin(years))].sort_values("age")
    _, ax = plt.subplots(figsize=(10, 5.5))
    palette = sns.color_palette("Reds_r", n_colors=len(years))
    for y, color in zip(years, palette):
        s = sub[sub["year"] == y]
        ax.plot(s["age"].astype(str), s["value"], marker="o",
                color=color, lw=2.2, label=str(y))
    ax.set_title("Japan: the M-curve flattens as female participation rises (1990-2024)")
    ax.set_xlabel("Age group")
    ax.set_ylabel("% of female population in age group")
    ax.legend(frameon=True, title="Year")
    sns.despine()
    plt.tight_layout()
    plt.savefig(os.path.join(FIG_DIR, "fig4_japan_mcurve_evolution.png"))
    plt.close()


# ================================================================== analysis
def report(wb: pd.DataFrame, ilo: pd.DataFrame):
    """Print the headline numerical findings (also documented in README)."""
    f = wb[wb["sex"] == "female"].pivot(index="year", columns="iso", values="value")
    p = wb.pivot_table(index=["iso", "year"], columns="sex", values="value")
    gap = (p["male"] - p["female"]).unstack("iso")

    lines = ["", "KEY FINDINGS", "============"]
    for iso, name in COUNTRIES.items():
        lines.append(
            f"{name}: female LFPR {f[iso].loc[1990]:.1f}% (1990) -> "
            f"{f[iso].iloc[-1]:.1f}% ({f.index[-1]}), "
            f"change {f[iso].iloc[-1] - f[iso].loc[1990]:+.1f} pp")
    for iso, name in COUNTRIES.items():
        lines.append(
            f"{name}: gender gap {gap[iso].loc[1990]:.1f} pp (1990) -> "
            f"{gap[iso].iloc[-1]:.1f} pp ({gap.index[-1]}), "
            f"narrowed by {gap[iso].loc[1990] - gap[iso].iloc[-1]:.1f} pp")

    # M-dip depth: participation at 25-29 minus participation at 30-34
    for year in [1990, 2024]:
        s = ilo[(ilo["sex"] == "female") & (ilo["year"] == year)]
        s = s.set_index(["country", "age"])["value"]
        for name in ["Japan", "Sweden"]:
            dip = s.loc[(name, "25-29")] - s.loc[(name, "30-34")]
            lines.append(f"{name} M-dip depth ({year}): {dip:+.1f} pp "
                         f"(25-29 minus 30-34)")
    # prime-age comparison
    s = ilo[(ilo["sex"] == "female") & (ilo["age"] == "25-29") & (ilo["year"] == 2024)]
    s = s.set_index("country")["value"]
    lines.append(f"2024, ages 25-29: Japan {s['Japan']:.1f}% vs Sweden {s['Sweden']:.1f}%")
    print("\n".join(lines))


def main():
    wb, ilo = load_data()
    fig1_trend(wb)
    fig2_age_profile(ilo)
    fig3_gender_gap(wb)
    fig4_japan_evolution(ilo)
    report(wb, ilo)
    print(f"\nFigures saved to {FIG_DIR}/")


if __name__ == "__main__":
    main()
