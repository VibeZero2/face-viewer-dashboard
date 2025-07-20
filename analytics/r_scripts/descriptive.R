#!/usr/bin/env Rscript

# Descriptive Statistics Script for Face Viewer Dashboard
# This script calculates basic descriptive statistics for facial perception data

# Command line arguments:
# 1. Input CSV file path
# 2. Output JSON file path
# 3. Variable name to analyze

# Load required libraries
suppressPackageStartupMessages({
  library(jsonlite)
})

# Parse command line arguments
args <- commandArgs(trailingOnly = TRUE)
input_file <- args[1]
output_file <- args[2]
variable_name <- args[3]

# Read the data
data <- read.csv(input_file, stringsAsFactors = FALSE)

# Calculate descriptive statistics
if (variable_name %in% colnames(data)) {
  variable_data <- data[[variable_name]]
  
  # Handle non-numeric data
  if (!is.numeric(variable_data)) {
    # For categorical data, calculate frequencies
    freq_table <- table(variable_data)
    result <- list(
      variable = variable_name,
      type = "categorical",
      n = length(variable_data),
      unique_values = length(unique(variable_data)),
      frequencies = as.list(freq_table),
      mode = names(freq_table)[which.max(freq_table)]
    )
  } else {
    # For numeric data, calculate standard descriptive statistics
    result <- list(
      variable = variable_name,
      type = "numeric",
      n = length(variable_data),
      mean = mean(variable_data, na.rm = TRUE),
      median = median(variable_data, na.rm = TRUE),
      sd = sd(variable_data, na.rm = TRUE),
      min = min(variable_data, na.rm = TRUE),
      max = max(variable_data, na.rm = TRUE),
      q1 = quantile(variable_data, 0.25, na.rm = TRUE),
      q3 = quantile(variable_data, 0.75, na.rm = TRUE)
    )
  }
} else {
  result <- list(
    error = paste("Variable", variable_name, "not found in dataset")
  )
}

# Write results to JSON file
write_json(result, output_file, pretty = TRUE)

# Print success message
cat("Descriptive statistics calculated successfully.\n")
