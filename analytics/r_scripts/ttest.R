#!/usr/bin/env Rscript

# T-Test Script for Face Viewer Dashboard
# This script performs t-tests for facial perception data

# Command line arguments:
# 1. Input CSV file path
# 2. Output JSON file path
# 3. First variable name
# 4. Second variable name (or grouping variable)
# 5. Test type: "paired", "independent", or "one-sample" (with optional reference value)

# Load required libraries
suppressPackageStartupMessages({
  library(jsonlite)
})

# Parse command line arguments
args <- commandArgs(trailingOnly = TRUE)
input_file <- args[1]
output_file <- args[2]
var1 <- args[3]
var2 <- args[4]
test_type <- args[5]
ref_value <- if (length(args) > 5) as.numeric(args[6]) else 0

# Read the data
data <- read.csv(input_file, stringsAsFactors = FALSE)

# Perform t-test based on test type
if (var1 %in% colnames(data)) {
  if (test_type == "one-sample") {
    # One-sample t-test
    t_result <- t.test(data[[var1]], mu = ref_value)
    result <- list(
      test_type = "one-sample t-test",
      variable = var1,
      reference_value = ref_value,
      t_statistic = t_result$statistic,
      df = t_result$parameter,
      p_value = t_result$p.value,
      confidence_interval = as.numeric(t_result$conf.int),
      mean = t_result$estimate,
      significant = t_result$p.value < 0.05
    )
  } else if (test_type == "paired" && var2 %in% colnames(data)) {
    # Paired t-test
    t_result <- t.test(data[[var1]], data[[var2]], paired = TRUE)
    result <- list(
      test_type = "paired t-test",
      variable1 = var1,
      variable2 = var2,
      t_statistic = t_result$statistic,
      df = t_result$parameter,
      p_value = t_result$p.value,
      confidence_interval = as.numeric(t_result$conf.int),
      mean_difference = as.numeric(t_result$estimate),
      significant = t_result$p.value < 0.05
    )
  } else if (test_type == "independent" && var2 %in% colnames(data)) {
    # Independent t-test (assuming var2 is a grouping variable)
    groups <- unique(data[[var2]])
    if (length(groups) == 2) {
      group1 <- data[data[[var2]] == groups[1], var1]
      group2 <- data[data[[var2]] == groups[2], var1]
      t_result <- t.test(group1, group2, var.equal = FALSE)
      result <- list(
        test_type = "independent t-test",
        variable = var1,
        grouping_variable = var2,
        group1 = groups[1],
        group2 = groups[2],
        t_statistic = t_result$statistic,
        df = t_result$parameter,
        p_value = t_result$p.value,
        confidence_interval = as.numeric(t_result$conf.int),
        mean_group1 = mean(group1, na.rm = TRUE),
        mean_group2 = mean(group2, na.rm = TRUE),
        significant = t_result$p.value < 0.05
      )
    } else {
      result <- list(
        error = "Grouping variable must have exactly 2 unique values for independent t-test"
      )
    }
  } else {
    result <- list(
      error = paste("Invalid test type or variable combination:", test_type, var1, var2)
    )
  }
} else {
  result <- list(
    error = paste("Variable", var1, "not found in dataset")
  )
}

# Write results to JSON file
write_json(result, output_file, pretty = TRUE)

# Print success message
cat("T-test completed successfully.\n")
