# =============================================================================
# Female Labor Force Participation: Japan vs. Sweden (1990-2025)
# -----------------------------------------------------------------------------
# Part A of the portfolio project. Reads the cached tidy CSVs under data/
# (no API calls — numbers are identical to the archived Python version) and
# reproduces figures fig1–fig4 with ggplot2. Prints the key numerical
# findings to the console.
#
# Run from the project directory:
#   Rscript analysis.R
#
# Required packages: tidyverse, scales
# =============================================================================

suppressPackageStartupMessages({
  library(tidyverse)
  library(scales)
})

# ------------------------------------------------------------------ paths
DATA_DIR <- "data"
FIG_DIR  <- "figures"
dir.create(FIG_DIR, showWarnings = FALSE)

# ------------------------------------------------------------------ style
JP_RED  <- "#BC002D"  # Japan
SE_BLUE <- "#006AA7"  # Sweden

theme_clean <- function() {
  theme_minimal(base_size = 12) +
    theme(
      plot.title = element_text(face = "bold", size = 14),
      plot.background = element_rect(fill = "white", color = NA),
      panel.background = element_rect(fill = "white", color = NA),
      legend.background = element_rect(fill = "white", color = "grey80")
    )
}

# ------------------------------------------------------------------ data
wb <- read_csv(file.path(DATA_DIR, "wb_lfpr_jpn_swe.csv"), show_col_types = FALSE)

age_levels <- c("15-19", "20-24", "25-29", "30-34", "35-39",
                "40-44", "45-49", "50-54", "55-59", "60-64")
ilo <- read_csv(file.path(DATA_DIR, "ilostat_age_lfpr_jpn_swe.csv"),
                show_col_types = FALSE) %>%
  mutate(age = factor(age, levels = age_levels, ordered = TRUE))

# ================================================================ figures

# ---- fig1: long-run female participation trends, Japan vs Sweden ----
fig1_trend <- function() {
  f <- wb %>% filter(sex == "female")
  last_pts <- f %>%
    group_by(country) %>%
    filter(year == max(year)) %>%
    ungroup()

  p <- ggplot(f, aes(x = year, y = value, color = country)) +
    geom_line(linewidth = 1.1) +
    geom_text(
      data = last_pts,
      aes(label = sprintf("%.1f%%", value)),
      hjust = -0.15, fontface = "bold", size = 4.2, show.legend = FALSE
    ) +
    scale_color_manual(values = c("Japan" = JP_RED, "Sweden" = SE_BLUE)) +
    scale_x_continuous(expand = expansion(mult = c(0.01, 0.08))) +
    labs(
      title = "Female labor force participation rate (ages 15+), 1990-2025",
      x = "Year", y = "% of female population ages 15+", color = NULL
    ) +
    theme_clean() +
    theme(legend.position = c(0.12, 0.88))

  ggsave(file.path(FIG_DIR, "fig1_female_lfpr_trend.png"), p,
         width = 10, height = 5.5, dpi = 150)
}

# ---- fig2: the M-curve — female participation by age, 2024 ----
fig2_age_profile <- function(year = 2024) {
  sub <- ilo %>% filter(sex == "female", year == !!year) %>% arrange(age)

  jp_vals <- sub %>% filter(country == "Japan")
  dip <- with(jp_vals,
              value[age == "25-29"] - value[age == "30-34"])
  dip_y <- with(jp_vals, value[age == "30-34"])

  # Position on the discrete age axis by index: "30-34" is level 4.
  # The text sits just right of the dip and an arrow points at it.
  p <- ggplot(sub, aes(x = age, y = value, color = country, group = country)) +
    geom_line(linewidth = 1.1) +
    geom_point(size = 2.5) +
    annotate(
      "text",
      x = 5.6, y = dip_y - 15,
      label = sprintf("Japan's M-dip: %.1f pp drop\nat ages 30-34", dip),
      size = 3.8, color = "black"
    ) +
    annotate(
      "segment",
      x = 5.0, xend = 4.05, y = dip_y - 8.5, yend = dip_y - 1,
      arrow = arrow(length = unit(0.25, "cm")), color = "black"
    ) +
    scale_color_manual(values = c("Japan" = JP_RED, "Sweden" = SE_BLUE)) +
    labs(
      title = sprintf("Female participation by age group, %d", year),
      subtitle = "Japan's M-curve vs Sweden's continuous profile",
      x = "Age group", y = "% of female population in age group", color = NULL
    ) +
    theme_clean() +
    theme(legend.position = c(0.88, 0.88),
          axis.text.x = element_text(angle = 30, hjust = 1))

  ggsave(file.path(FIG_DIR, "fig2_age_profile_mcurve.png"), p,
         width = 10, height = 5.5, dpi = 150)
}

# ---- fig3: gender gap (male minus female) over time ----
fig3_gender_gap <- function() {
  gap <- wb %>%
    pivot_wider(names_from = sex, values_from = value) %>%
    mutate(gap = male - female)
  last_pts <- gap %>%
    group_by(country) %>%
    filter(year == max(year)) %>%
    ungroup()

  p <- ggplot(gap, aes(x = year, y = gap, color = country)) +
    geom_line(linewidth = 1.1) +
    geom_hline(yintercept = 0, linetype = "dashed", color = "grey50") +
    geom_text(
      data = last_pts,
      aes(label = sprintf("%.1f pp", gap)),
      hjust = -0.15, fontface = "bold", size = 4.2, show.legend = FALSE
    ) +
    scale_color_manual(values = c("Japan" = JP_RED, "Sweden" = SE_BLUE)) +
    scale_x_continuous(expand = expansion(mult = c(0.01, 0.08))) +
    labs(
      title = "Gender gap in labor force participation (male minus female), 1990-2025",
      x = "Year", y = "Percentage points", color = "Country"
    ) +
    theme_clean() +
    theme(legend.position = c(0.88, 0.88))

  ggsave(file.path(FIG_DIR, "fig3_gender_gap.png"), p,
         width = 10, height = 5.5, dpi = 150)
}

# ---- fig4: Japan's M-curve flattening, 1990 -> 2024 ----
fig4_japan_evolution <- function() {
  years <- c(1990, 2000, 2010, 2024)
  sub <- ilo %>%
    filter(country == "Japan", sex == "female", year %in% years) %>%
    arrange(age) %>%
    mutate(year = factor(year, levels = years))
  reds <- c("1990" = "#FCAE91", "2000" = "#FB6A4A",
            "2010" = "#DE2D26", "2024" = "#99000D")

  p <- ggplot(sub, aes(x = age, y = value, color = year, group = year)) +
    geom_line(linewidth = 1.1) +
    geom_point(size = 2.2) +
    scale_color_manual(values = reds) +
    labs(
      title = "Japan: the M-curve flattens as female participation rises (1990-2024)",
      x = "Age group", y = "% of female population in age group", color = "Year"
    ) +
    theme_clean() +
    theme(legend.position = c(0.88, 0.85),
          axis.text.x = element_text(angle = 30, hjust = 1))

  ggsave(file.path(FIG_DIR, "fig4_japan_mcurve_evolution.png"), p,
         width = 10, height = 5.5, dpi = 150)
}

# ================================================================ report
report <- function() {
  f <- wb %>%
    filter(sex == "female") %>%
    select(iso, country, year, value)
  gap <- wb %>%
    pivot_wider(names_from = sex, values_from = value) %>%
    mutate(gap = male - female)

  cat("\nKEY FINDINGS\n============\n")
  for (cc in c("Japan", "Sweden")) {
    s <- f %>% filter(country == cc) %>% arrange(year)
    cat(sprintf("%s: female LFPR %.1f%% (1990) -> %.1f%% (%d), change %+.1f pp\n",
                cc, s$value[s$year == 1990], tail(s$value, 1),
                tail(s$year, 1), tail(s$value, 1) - s$value[s$year == 1990]))
  }
  for (cc in c("Japan", "Sweden")) {
    s <- gap %>% filter(country == cc) %>% arrange(year)
    cat(sprintf("%s: gender gap %.1f pp (1990) -> %.1f pp (%d), narrowed by %.1f pp\n",
                cc, s$gap[s$year == 1990], tail(s$gap, 1),
                tail(s$year, 1), s$gap[s$year == 1990] - tail(s$gap, 1)))
  }
  for (yr in c(1990, 2024)) {
    for (cc in c("Japan", "Sweden")) {
      s <- ilo %>% filter(country == cc, sex == "female", year == yr)
      dip <- s$value[s$age == "25-29"] - s$value[s$age == "30-34"]
      cat(sprintf("%s M-dip depth (%d): %+.1f pp (25-29 minus 30-34)\n",
                  cc, yr, dip))
    }
  }
  s <- ilo %>% filter(sex == "female", age == "25-29", year == 2024)
  cat(sprintf("2024, ages 25-29: Japan %.1f%% vs Sweden %.1f%%\n",
              s$value[s$country == "Japan"], s$value[s$country == "Sweden"]))
}

# ================================================================== main
fig1_trend()
fig2_age_profile()
fig3_gender_gap()
fig4_japan_evolution()
report()
cat(sprintf("\nFigures saved to %s/\n", FIG_DIR))
