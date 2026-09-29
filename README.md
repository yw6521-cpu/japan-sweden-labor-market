# Female Labor Force Participation: Japan vs. Sweden (1990–2025)

A data-analysis project comparing women's labor market attachment in Japan and
Sweden over three decades — rebuilt in R as a portfolio piece
(originally written in R as university coursework; the original code was
later found and its logic folded into Part B below).

> **Note:** an earlier Python rebuild of this project is archived under
> `python_archive/` (kept for reference only). The R version here is the
> current, canonical one.

## Key findings

**1. Japan caught up dramatically; Sweden started high and stayed high.**
Female labor force participation (ages 15+) rose from **50.1% to 55.9%
(+5.8 pp)** in Japan between 1990 and 2025, while Sweden edged from
**62.8% to 61.5% (−1.3 pp)** — Sweden's slight decline reflects an aging
population rather than weaker attachment (see finding 3).

**2. The gender gap narrowed far faster in Japan.**
The male-minus-female participation gap fell from **27.2 pp to 15.6 pp
(−11.7 pp)** in Japan vs. **8.6 pp to 6.1 pp (−2.5 pp)** in Sweden.

**3. Japan's "M-curve" is flattening; Sweden never had one.**
Plotting participation by 5-year age band reveals Japan's classic M-shape:
women exit the labor force in their early 30s (childcare ages) and return
later. The dip (participation at 25–29 minus 30–34) shrank from
**9.7 pp in 1990 to 5.0 pp in 2024**. Sweden's curve rises continuously
through the 30s and 40s — no dip at any point in 1990–2024.

**4. Young Japanese women now out-participate young Swedish women.**
At ages 25–29 in 2024: **Japan 88.9% vs. Sweden 83.9%**.

**Interpretation.** The contrast is consistent with institutional differences:
Sweden's parental-leave and public-childcare system supports continuous
careers, while Japan's historical pattern combined career breaks with
re-entry into non-regular employment — a structure that is visibly eroding
as the M-curve flattens.

## Data sources

| Dataset | Source | Indicator | Coverage |
|---|---|---|---|
| Headline participation rates | [World Bank API](https://api.worldbank.org/v2) (no key required) | `SL.TLF.CACT.FE.ZS` (female), `SL.TLF.CACT.MA.ZS` (male) — labor force participation, % of population ages 15+, modeled ILO estimate | Japan, Sweden, 1990–2025 |
| Participation by 5-year age band | [ILOSTAT SDMX API](https://sdmx.ilo.org) (no key required) | `EAP_DWAP_SEX_AGE_RT` — labour force participation rate by sex and age, sourced from national Labour Force Surveys (Japan: Statistics Bureau LFS; Sweden: EU-LFS) | Japan, Sweden, 1990–2024 |

The R scripts read the cached tidy CSVs under `data/` directly (no API
calls at run time), so the analysis is fully reproducible and the numbers
match the charts exactly. Note the two sources use slightly
different estimation methods, so headline levels are compared within — not
across — sources.

## Methods

- `analysis.R` reads the cached CSVs in `data/` with `readr`, tidies with
  `dplyr`/`tidyr`, and prints the headline statistics quoted above to the
  console.
- Four charts are produced with `ggplot2` (see `figures/`):
  1. `fig1_female_lfpr_trend.png` — long-run female participation, 1990–2025
  2. `fig2_age_profile_mcurve.png` — age profiles in 2024: Japan's M-curve vs. Sweden's continuous curve
  3. `fig3_gender_gap.png` — male–female participation gap, 1990–2025
  4. `fig4_japan_mcurve_evolution.png` — Japan's M-curve flattening, 1990 → 2024

## How to run

Requires R (≥ 4.0) with the `tidyverse` and `scales` packages:

```r
install.packages(c("tidyverse", "scales"))
```

Then, from the project directory:

```bash
Rscript analysis.R                 # Part A: participation rates & M-curve
Rscript analysis_nonregular.R      # Part B: non-regular employment structure
```

Figures are written to `figures/`.

## Project structure

```
├── analysis.R                      # Part A: load → clean → analyze → chart
├── analysis_nonregular.R           # Part B: non-regular employment (Japan/Sweden)
├── README.md
├── data/
│   ├── wb_lfpr_jpn_swe.csv           # cached World Bank response (Part A)
│   ├── ilostat_age_lfpr_jpn_swe.csv  # cached ILOSTAT response (Part A)
│   ├── estat_nonregular_jpn.csv      # e-Stat LFS Table 1-2-4, Japan (Part B)
│   └── jpn_nonregular_2024_tidy.csv  # tidy non-regular shares, Japan 2024 (Part B)
├── figures/
│   ├── fig1_female_lfpr_trend.png
│   ├── fig2_age_profile_mcurve.png
│   ├── fig3_gender_gap.png
│   ├── fig4_japan_mcurve_evolution.png
│   ├── fig5_japan_nonregular_by_age_sex.png
│   ├── fig6_sweden_temporary_by_age_sex.png
│   └── fig7_youth_nonregular_comparison.png
└── python_archive/                   # earlier Python rebuild, kept for reference
    ├── analysis.py
    ├── analysis_nonregular.py
    └── requirements-python.txt
```

## Part B – Non-regular employment structure

A second pillar rebuilt from the original coursework scripts
(`nonregular.R` and `part_time_sweden.R`, originally written in R):
how non-regular and temporary employment is distributed by age and sex
in Japan and Sweden in 2024 — the employment-quality counterpart to
Part A's participation story.

### Key findings

**1. In Japan, non-regular work is a women's story — and it grows
with age.** The non-regular share of female employees rises from
**30.0% at ages 25–34 to 53.2% at 45–54, 64.3% at 55–64, and 83.5%
at 65+**. Men stay below 15% through prime working ages (25–54) and
only reach high shares at 55–64 (23.9%) and 65+ (71.3%, reflecting
post-retirement re-employment). The 65+ gender gap is 12.2 pp.

**2. In Sweden, temporary work is a youth story.** **55.9% of female
and 45.3% of male employees aged 15–24** are temporary — but the
share collapses to about 10% by ages 25–49 and ~5% by 50–59.

**3. Young workers look alike across both countries.** At ages 15–24,
Japan's non-regular share (female 54.6%, male 49.3%) is close to
Sweden's temporary share (female 55.9%, male 45.3%) — both countries
channel labor-market flexibility through their youngest workers.

### Data sources

| Dataset | Source | Coverage |
|---|---|---|
| Non-regular employment by age & sex | [e-Stat](https://www.e-stat.go.jp), Labour Force Survey, Table 1-2-4 | Japan, 2024; non-regular staff as % of employees excl. executives |
| Temporary employment by age & sex | 2024 quarterly averages compiled from Eurostat (hand-compiled in the original coursework) | Sweden, 2024; temporary employees as % of all employees |

Note: Japan's "non-regular" and Sweden's "temporary" follow different
national definitions, so cross-country levels are not strictly
comparable — each is best read within its own definition. The
comparison chart (fig7) is therefore limited to the one age band
(15–24) measured on the same basis in both datasets.

### Methods

- `analysis_nonregular.R` reads the tidy e-Stat cache from `data/`
  (`jpn_nonregular_2024_tidy.csv`), uses the Sweden quarterly averages
  compiled in the original coursework, and prints the headline
  statistics quoted above to the console.
- Three charts are produced with `ggplot2` (see `figures/`):
  5. `fig5_japan_nonregular_by_age_sex.png` — Japan non-regular share by age & sex, 2024
  6. `fig6_sweden_temporary_by_age_sex.png` — Sweden temporary share by age & sex, 2024
  7. `fig7_youth_nonregular_comparison.png` — young workers (15–24): Japan vs. Sweden
