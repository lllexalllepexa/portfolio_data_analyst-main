# R: descriptive stats + ANOVA + ggplot2 visualization
# Usage: Rscript r/analysis.R

suppressPackageStartupMessages({
  library(dplyr)
  library(ggplot2)
  library(readr)
})

args <- commandArgs(trailingOnly = FALSE)
file_arg <- grep("^--file=", args, value = TRUE)
root <- if (length(file_arg)) {
  normalizePath(file.path(dirname(sub("^--file=", "", file_arg)), ".."), winslash = "/")
} else {
  normalizePath(getwd(), winslash = "/")
}
parquet <- file.path(root, "data", "processed", "orders_clean.parquet")
csv_raw <- file.path(root, "data", "raw", "global_superstore.csv")

if (file.exists(parquet)) {
  if (!requireNamespace("arrow", quietly = TRUE)) {
    stop("Install arrow: install.packages('arrow')")
  }
  df <- arrow::read_parquet(parquet)
} else if (file.exists(csv_raw)) {
  df <- read_csv(csv_raw, show_col_types = FALSE)
  df$Sales <- as.numeric(df$Sales)
  df$Profit <- as.numeric(df$Profit)
  df$Discount <- as.numeric(df$Discount)
} else {
  stop(paste0(
    "Нет данных. Запустите: python -m superstore.etl.load_and_clean\n",
    "or place CSV at: ", csv_raw
  ))
}

# Normalize column names if raw CSV
if ("Sales" %in% names(df)) {
  df <- df %>%
    rename(
      sales = Sales,
      profit = Profit,
      discount = Discount,
      region = Region,
      category = Category,
      segment = Segment
    )
}

cat("=== Сводка (R) ===\n")
print(summary(df[, c("sales", "profit", "discount")]))

# ANOVA: profit across segments
fit <- aov(profit ~ segment, data = df)
cat("\n=== ANOVA: прибыль ~ сегмент ===\n")
print(summary(fit))

# ggplot: profit margin by category
p <- df %>%
  filter(!is.na(sales), sales > 0) %>%
  mutate(margin = profit / sales) %>%
  group_by(category) %>%
  summarise(margin = median(margin, na.rm = TRUE), .groups = "drop") %>%
  ggplot(aes(reorder(category, margin), margin)) +
  geom_col(fill = "#2E86AB") +
  coord_flip() +
  labs(
    title = "Медианная маржа по категориям",
    x = NULL, y = "Медианная маржа"
  ) +
  theme_minimal()

out <- file.path(root, "data", "processed", "figures", "margin_by_category_r.png")
dir.create(dirname(out), recursive = TRUE, showWarnings = FALSE)
ggsave(out, p, width = 8, height = 5, dpi = 120)
cat("\nСохранено:", out, "\n")
