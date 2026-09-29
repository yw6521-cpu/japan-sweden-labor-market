# =============================================================================
# Non-regular Employment Structure: Japan vs. Sweden (2024)
# -----------------------------------------------------------------------------
# Part B of the portfolio project. A cleaned-up version of the original
# coursework scripts (nonregular.R and part_time_sweden.R):
#   * Japan: non-regular share of employees by age and sex, 2024 —
#     read from the tidy cache in data/ (originally computed from the
#     e-Stat Labour Force Survey, Table 1-2-4)
#   * Sweden: temporary share of employees by age and sex, 2024 —
#     quarterly averages compiled from Eurostat (hand-compiled in the
#     original coursework)
# Reproduces figures fig5–fig7 with ggplot2 in the same clean style as
# Part A (white background). Prints the key numerical findings.
#
# Run from the project directory:
#   Rscript analysis_nonregular.R
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
JP_RED  <- "#BC002D"  # Japan accent (matches Part A)
SE_BLUE <- "#006AA7"  # Sweden accent (matches Part A)
FEMALE  <- "#C0392B"  # female bars
MALE    <- "#2E6E8E"  # male bars

theme_clean <- function() {
  theme_minimal(base_size = 12) +
    theme(
      plot.title = element_text(face = "bold", size = 13),
      plot.background = element_rect(fill = "white", color = NA),
      panel.background = element_rect(fill = "white", color = NA),
      plot.caption = element_text(hjust = 0, size = 8, color = "#666666"),
      legend.background = element_rect(fill = "white", color = "grey80")
    )
}

# ------------------------------------------------------------------ data
# Tidy cache written by the archived Python build: Sex, age_label, share.
# Age labels may use en/em dashes; normalize before matching.
jpn <- read_csv(file.path(DATA_DIR, "jpn_nonregular_2024_tidy.csv"),
                show_col_types = FALSE) %>%
  mutate(
    age_std = age_label %>%
      str_replace_all("\u2013|\u2014|\u2212", "-") %>%
      str_replace("65-", "65+"),
    age_band = factor(
      age_std,
      levels = c("65+", "55-64", "45-54", "35-44", "25-34", "15-24"),
      labels = c("65+", "55-64", "45-54", "35-44", "25-34", "15-24")
    ),
    Sex = factor(Sex, levels = c("Female", "Male"))
  )
stopifnot(nrow(jpn) == 12, !any(is.na(jpn$share)), !any(is.na(jpn$age_band)))

# Sweden: 2024 quarterly averages of temporary employees as % of all
# employees, compiled from Eurostat (see original part_time_sweden.R).
sweden <- tibble(
  age_band = factor(c("15-24", "25-49", "50-59"),
                    levels = c("50-59", "25-49", "15-24")),
  Female = c(55.95, 10.30, 5.28),
  Male   = c(45.30, 8.95, 3.55)
) %>%
  pivot_longer(c(Female, Male), names_to = "Sex", values_to = "temp_share") %>%
  mutate(
    Sex = factor(Sex, levels = c("Female", "Male")),
    share = temp_share / 100
  )

# ================================================================ figures

# ---- fig5: Japan non-regular share by age and sex, 2024 ----
fig5_japan <- function() {
  p <- ggplot(jpn, aes(x = share, y = age_band, fill = Sex)) +
    geom_col(position = position_dodge(width = 0.75), width = 0.6) +
    geom_text(
      aes(label = percent(share, accuracy = 1)),
      position = position_dodge(width = 0.75),
      hjust = -0.12, size = 3.4, color = "#333333"
    ) +
    scale_x_continuous(
      labels = percent_format(accuracy = 1),
      limits = c(0, 1.0), expand = expansion(mult = c(0, 0.02))
    ) +
    scale_fill_manual(values = c("Female" = FEMALE, "Male" = MALE)) +
    labs(
      title = "Non-regular employment in Japan by age group and sex, 2024",
      x = "Non-regular staff (% of employees excl. executives)",
      y = NULL, fill = NULL,
      caption = "Source: e-Stat, Labour Force Survey, Table 1-2-4 (2024)."
    ) +
    theme_clean() +
    theme(legend.position = c(0.88, 0.18))

  ggsave(file.path(FIG_DIR, "fig5_japan_nonregular_by_age_sex.png"), p,
         width = 9, height = 5.2, dpi = 150)
}

# ---- fig6: Sweden temporary share by age and sex, 2024 ----
fig6_sweden <- function() {
  p <- ggplot(sweden, aes(x = share, y = age_band, fill = Sex)) +
    geom_col(position = position_dodge(width = 0.75), width = 0.6) +
    geom_text(
      aes(label = percent(share, accuracy = 1)),
      position = position_dodge(width = 0.75),
      hjust = -0.12, size = 3.4, color = "#333333"
    ) +
    scale_x_continuous(
      labels = percent_format(accuracy = 1),
      limits = c(0, 0.70), expand = expansion(mult = c(0, 0.02))
    ) +
    scale_fill_manual(values = c("Female" = FEMALE, "Male" = MALE)) +
    labs(
      title = "Temporary employment in Sweden by age group and sex, 2024",
      x = "Temporary employees (% of all employees, 2024 average)",
      y = NULL, fill = NULL,
      caption = paste(
        "Source: Eurostat quarterly data, compiled as 2024 average",
        "(from original coursework)."
      )
    ) +
    theme_clean() +
    theme(legend.position = c(0.88, 0.82))

  ggsave(file.path(FIG_DIR, "fig6_sweden_temporary_by_age_sex.png"), p,
         width = 9, height = 4.2, dpi = 150)
}

# ---- fig7: young workers (15–24) in Japan vs Sweden ----
fig7_youth <- function() {
  jpn_youth <- jpn %>%
    filter(age_std == "15-24") %>%
    select(Sex, share) %>%
    mutate(country = "Japan")
  swe_youth <- tibble(
    Sex = factor(c("Female", "Male"), levels = c("Female", "Male")),
    share = c(0.5595, 0.4530),
    country = "Sweden"
  )
  youth <- bind_rows(jpn_youth, swe_youth) %>%
    mutate(
      grp = factor(
        paste(country, Sex, sep = " - "),
        levels = c("Japan - Female", "Japan - Male",
                   "Sweden - Female", "Sweden - Male")
      )
    )
  # Male bars use a lighter shade of the country color (ggplot-native
  # equivalent of the hatched male bars in the archived Python version).
  grp_colors <- c(
    "Japan - Female" = JP_RED,   "Japan - Male" = "#E8A0A8",
    "Sweden - Female" = SE_BLUE, "Sweden - Male" = "#8FBCD8"
  )

  p <- ggplot(youth, aes(x = share, y = grp, fill = grp)) +
    geom_col(width = 0.55) +
    geom_text(
      aes(label = percent(share, accuracy = 0.1)),
      hjust = -0.12, size = 4, color = "#333333"
    ) +
    scale_x_continuous(
      labels = percent_format(accuracy = 1),
      limits = c(0, max(youth$share) * 1.25),
      expand = expansion(mult = c(0, 0.02))
    ) +
    scale_fill_manual(values = grp_colors, guide = "none") +
    labs(
      title = "Young workers (15-24) in non-regular / temporary jobs, 2024",
      x = "Non-regular / temporary share of employees (%)",
      y = NULL,
      caption = paste(
        "Sources: Japan - e-Stat LFS Table 1-2-4 (non-regular staff, excl. executives);\n",
        "Sweden - Eurostat quarterly average (temporary employees).\n",
        "Note: definitions differ across countries. Lighter bars = male."
      )
    ) +
    theme_clean()

  ggsave(file.path(FIG_DIR, "fig7_youth_nonregular_comparison.png"), p,
         width = 7.5, height = 4.4, dpi = 150)
}

# ================================================================ report
report <- function() {
  piv <- jpn %>%
    select(Sex, age_band, share) %>%
    pivot_wider(names_from = Sex, values_from = share)

  cat("Japan non-regular share by age group and sex, 2024:\n")
  print(as.data.frame(piv), row.names = FALSE)
  cat("\n")

  get <- function(age, sex)
    jpn$share[jpn$age_std == age & jpn$Sex == sex]
  f65 <- get("65+", "Female"); m65 <- get("65+", "Male")
  cat(sprintf("Japan 65+: female %.1f%%, male %.1f%% (gap %.1f pp)\n",
              f65 * 100, m65 * 100, (f65 - m65) * 100))
  f24 <- get("15-24", "Female"); m24 <- get("15-24", "Male")
  cat(sprintf("Japan 15-24: female %.1f%%, male %.1f%%\n",
              f24 * 100, m24 * 100))
  cat("Sweden temporary 15-24: female 55.9%, male 45.3%\n")
  cat(sprintf(paste0("Youth (15-24) Japan vs Sweden — female %.1f%% vs 55.9%%, ",
                     "male %.1f%% vs 45.3%%\n"),
              f24 * 100, m24 * 100))
}

# ================================================================== main
fig5_japan()
fig6_sweden()
fig7_youth()
report()
cat(sprintf("\nFigures saved to %s/\n", FIG_DIR))
