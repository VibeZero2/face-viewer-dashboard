#!/usr/bin/env Rscript

# ANOVA Script for Face Viewer Dashboard
# This script performs ANOVA tests for facial perception data

# Command line arguments:
# 1. Input CSV file path
# 2. Output JSON file path
# 3. Dependent variable name
# 4. Independent variable name (grouping variable)

# Load required libraries
suppressPackageStartupMessages({
  library(jsonlite)
})

# Parse command line arguments
args <- commandArgs(trailingOnly = TRUE)
input_file <- args[1]
output_file <- args[2]
dependent_var <- args[3]
independent_var <- args[4]

# Read the data
data <- read.csv(input_file, stringsAsFactors = FALSE)

# Perform ANOVA
if (dependent_var %in% colnames(data) && independent_var %in% colnames(data)) {
  # Convert independent variable to factor if it's not already
  data[[independent_var]] <- as.factor(data[[independent_var]])
  
  # Create formula for ANOVA
  formula <- as.formula(paste(dependent_var, "~", independent_var))
  
  # Run ANOVA
  anova_result <- aov(formula, data = data)
  anova_summary <- summary(anova_result)[[1]]
  
  # Extract results
  result <- list(
    test_type = "ANOVA",
    dependent_variable = dependent_var,
    independent_variable = independent_var,
    f_statistic = anova_summary$`F value`[1],
    df = c(anova_summary$Df[1], anova_summary$Df[2]),
    p_value = anova_summary$`Pr(>F)`[1],
    significant = anova_summary$`Pr(>F)`[1] < 0.05,
    group_means = tapply(data[[dependent_var]], data[[independent_var]], mean, na.rm = TRUE),
    group_counts = tapply(data[[dependent_var]], data[[independent_var]], length)
  )
  
  # Add post-hoc test if ANOVA is significant
  if (result$significant) {
    # Perform Tukey's HSD test
    tukey_result <- TukeyHSD(anova_result)
    tukey_data <- tukey_result[[1]]
    
    # Convert to list format
    tukey_list <- list()
    for (i in 1:nrow(tukey_data)) {
      row_name <- rownames(tukey_data)[i]
      tukey_list[[row_name]] <- list(
        diff = tukey_data[i, "diff"],
        lower_ci = tukey_data[i, "lwr"],
        upper_ci = tukey_data[i, "upr"],
        p_adj = tukey_data[i, "p adj"],
        significant = tukey_data[i, "p adj"] < 0.05
      )
    }
    
    result$post_hoc <- list(
      test = "Tukey HSD",
      comparisons = tukey_list
    )
  }
} else {
  result <- list(
    error = paste("Variables not found in dataset:", 
                  if (!(dependent_var %in% colnames(data))) dependent_var else "",
                  if (!(independent_var %in% colnames(data))) independent_var else "")
  )
}

# Write results to JSON file
write_json(result, output_file, pretty = TRUE)

# Print success message
cat("ANOVA completed successfully.\n")
