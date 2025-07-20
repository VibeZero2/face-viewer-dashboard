#!/usr/bin/env Rscript

# Correlation Script for Face Viewer Dashboard
# This script performs correlation analyses for facial perception data

# Command line arguments:
# 1. Input CSV file path
# 2. Output JSON file path
# 3. First variable name
# 4. Second variable name
# 5. Correlation method (optional): "pearson", "spearman", or "kendall" (default: "pearson")

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
method <- if (length(args) > 4) args[5] else "pearson"

# Read the data
data <- read.csv(input_file, stringsAsFactors = FALSE)

# Perform correlation analysis
if (var1 %in% colnames(data) && var2 %in% colnames(data)) {
  # Check if variables are numeric
  if (is.numeric(data[[var1]]) && is.numeric(data[[var2]])) {
    # Run correlation test
    cor_result <- cor.test(data[[var1]], data[[var2]], method = method)
    
    # Extract results
    result <- list(
      test_type = paste(method, "correlation"),
      variable1 = var1,
      variable2 = var2,
      correlation = cor_result$estimate,
      statistic = cor_result$statistic,
      p_value = cor_result$p.value,
      confidence_interval = as.numeric(cor_result$conf.int),
      significant = cor_result$p.value < 0.05
    )
    
    # Add additional information
    result$interpretation <- list(
      strength = case_when(
        abs(result$correlation) < 0.3 ~ "weak",
        abs(result$correlation) < 0.7 ~ "moderate",
        TRUE ~ "strong"
      ),
      direction = if(result$correlation > 0) "positive" else "negative"
    )
    
    # Create scatterplot data for visualization
    scatter_data <- list()
    for (i in 1:min(100, nrow(data))) {  # Limit to 100 points for efficiency
      scatter_data[[i]] <- list(
        x = data[[var1]][i],
        y = data[[var2]][i]
      )
    }
    result$scatter_data <- scatter_data
    
  } else {
    result <- list(
      error = "Both variables must be numeric for correlation analysis"
    )
  }
} else {
  result <- list(
    error = paste("Variables not found in dataset:", 
                  if (!(var1 %in% colnames(data))) var1 else "",
                  if (!(var2 %in% colnames(data))) var2 else "")
  )
}

# Define case_when function (simplified version of dplyr's case_when)
case_when <- function(condition1, value1, condition2 = NULL, value2 = NULL, ...) {
  if (condition1) {
    return(value1)
  } else if (!is.null(condition2) && condition2) {
    return(value2)
  } else {
    args <- list(...)
    if (length(args) > 0) {
      return(args[[1]])
    } else {
      return(NULL)
    }
  }
}

# Write results to JSON file
write_json(result, output_file, pretty = TRUE)

# Print success message
cat("Correlation analysis completed successfully.\n")
