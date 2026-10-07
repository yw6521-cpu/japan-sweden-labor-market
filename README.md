# Female Labor Force Participation: Japan vs. Sweden (1968–2025)

A data-analysis project comparing women's labor market attachment in Japan and
Sweden over nearly six decades — rebuilt in R as a portfolio piece
(originally written in R as university coursework; the original code was
later found and its logic folded into Part B below).

> **Note:** an earlier Python rebuild of this project is archived under
> `python_archive/` (kept for reference only). The R version here is the
> current, canonical one.

## Key findings

**1. Both countries started near 50% in 1968 — then diverged sharply.**
Female labor force participation (ages 15+) rose from **50.5% to 73.3%
(+22.8 pp)** in Sweden between 1968 and 2025, but only from **50.7% to
56.4% (+5.7 pp)** in Japan. Sweden's rise reflects decades of
parental-leave and public-childcare policy supporting continuous careers;
Japan's slower climb came largely from women re-entering as non-regular
workers (see Part B).

**2. The gender gap narrowed far faster in Sweden.**
The male-minus-female participation gap fell from **31.5 pp to 4.7 pp
(−26.8 pp)** in Sweden vs. **31.4 pp to 15.3 pp (−16.1 pp)** in Japan
between 1968 and 2025 — both countries started from the same ~31 pp gap.

**3. Japan's "M-curve" deepened, then flattened; Sweden's never took hold.**
Plotting participation by 5-year age band reveals Japan's classic M-shape:
women exit the labor force in their early 30s (childcare ages) and return
later. The dip (participation at 25–29 minus 30–34) widened from
**9.7 pp in 1990 to a peak of 13.4 pp in 1998**, then shrank to
**5.0 pp in 2024**. Sweden's curve rises continuously through the 30s and
40s — the dip has been negative (i.e., no dip at all) in every year since
1985.

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
| Headline participation rates (15+) | [OECD Data Explorer](https://data-explorer.oecd.org/) via the [OECD SDMX API](https://sdmx.oecd.org/public/rest/v1/) (no key required) | "Employment and unemployment by five-year age group and sex – indicators": `LF_RATE` (labour force participation rate), `% of population`, age `_T` (total 15+) | Japan 1968–2025, Sweden 1963–2025 |
| Participation by 5-year age band | Same OECD dataset & API | Same indicator, ages 15–19 … 60–64 and 65+ | Japan 1968–2025, Sweden 1963–2025 |

The R scripts read the cached tidy CSVs under `data/` directly (no API
calls at run time), so the analysis is fully reproducible and the numbers
match the charts exactly. Both Part A series come from the single OECD
dataset above (national Labour Force Surveys: Japan's Statistics Bureau
LFS via e-Stat; Sweden's EU-LFS), so headline levels and age profiles are
directly comparable. Cached API responses: `oecd_lfpr_jpn_swe.csv`
(15+ totals) and `oecd_lfpr_jpn_swe_age.csv` (5-year bands).

## Methods

- `analysis.R` reads the cached OECD CSVs in `data/` with `readr`
  (`oecd_lfpr_jpn_swe.csv` for 15+ totals, `oecd_lfpr_jpn_swe_age.csv`
  for 5-year bands), tidies with `dplyr`/`tidyr`, and prints the headline
  statistics quoted above to the console.
- Four charts are produced with `ggplot2` (see `figures/`):
  1. `fig1_female_lfpr_trend.png` — long-run female participation, 1968–2025
  2. `fig2_age_profile_mcurve.png` — age profiles in 2024: Japan's M-curve vs. Sweden's continuous curve
  3. `fig3_gender_gap.png` — male–female participation gap, 1968–2025
  4. `fig4_japan_mcurve_evolution.png` — Japan's M-curve deepens then flattens, 1990 → 2024

## How to run

Requires R (≥ 4.0) with the tidyverse core packages and `scales`:

```r
install.packages(c("ggplot2", "dplyr", "tidyr", "readr", "scales"))
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
│   ├── oecd_lfpr_jpn_swe.csv           # cached OECD response, 15+ totals (Part A)
│   ├── oecd_lfpr_jpn_swe_age.csv      # cached OECD response, 5-year age bands (Part A)
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
