#!/usr/bin/env Rscript

# Regression Script for Face Viewer Dashboard
# This script performs linear regression analyses for facial perception data

# Command line arguments:
# 1. Input CSV file path
# 2. Output JSON file path
# 3. Dependent variable name
# 4. Independent variable(s) (comma-separated if multiple)

# Load required libraries
suppressPackageStartupMessages({
  library(jsonlite)
})

# Parse command line arguments
args <- commandArgs(trailingOnly = TRUE)
input_file <- args[1]
output_file <- args[2]
dependent_var <- args[3]
independent_vars <- unlist(strsplit(args[4], ","))

# Read the data
data <- read.csv(input_file, stringsAsFactors = FALSE)

# Check if variables exist in the dataset
all_vars <- c(dependent_var, independent_vars)
missing_vars <- all_vars[!all_vars %in% colnames(data)]

if (length(missing_vars) == 0) {
  # Create formula for regression
  formula_str <- paste(dependent_var, "~", paste(independent_vars, collapse = " + "))
  formula <- as.formula(formula_str)
  
  # Run regression
  reg_model <- lm(formula, data = data)
  reg_summary <- summary(reg_model)
  
  # Extract coefficients
  coef_data <- reg_summary$coefficients
  coefficients <- list()
  for (i in 1:nrow(coef_data)) {
    var_name <- rownames(coef_data)[i]
    coefficients[[var_name]] <- list(
      estimate = coef_data[i, "Estimate"],
      std_error = coef_data[i, "Std. Error"],
      t_value = coef_data[i, "t value"],
      p_value = coef_data[i, "Pr(>|t|)"],
      significant = coef_data[i, "Pr(>|t|)"] < 0.05
    )
  }
  
  # Extract model fit statistics
  result <- list(
    test_type = "linear_regression",
    dependent_variable = dependent_var,
    independent_variables = independent_vars,
    formula = formula_str,
    coefficients = coefficients,
    r_squared = reg_summary$r.squared,
    adj_r_squared = reg_summary$adj.r.squared,
    f_statistic = reg_summary$fstatistic[1],
    df = c(reg_summary$fstatistic[2], reg_summary$fstatistic[3]),
    p_value = pf(reg_summary$fstatistic[1], 
                 reg_summary$fstatistic[2], 
                 reg_summary$fstatistic[3], 
                 lower.tail = FALSE),
    significant = pf(reg_summary$fstatistic[1], 
                     reg_summary$fstatistic[2], 
                     reg_summary$fstatistic[3], 
                     lower.tail = FALSE) < 0.05
  )
  
  # Add predicted vs actual data for visualization
  predicted <- predict(reg_model)
  actual <- data[[dependent_var]]
  
  scatter_data <- list()
  for (i in 1:min(100, length(predicted))) {  # Limit to 100 points for efficiency
    scatter_data[[i]] <- list(
      predicted = predicted[i],
      actual = actual[i]
    )
  }
  result$scatter_data <- scatter_data
  
  # Add residual analysis
  residuals <- residuals(reg_model)
  result$residuals <- list(
    mean = mean(residuals),
    median = median(residuals),
    min = min(residuals),
    max = max(residuals),
    std_dev = sd(residuals),
    shapiro_test = list(
      statistic = shapiro.test(residuals)$statistic,
      p_value = shapiro.test(residuals)$p.value,
      normal = shapiro.test(residuals)$p.value > 0.05
    )
  )
  
} else {
  result <- list(
    error = paste("Variables not found in dataset:", paste(missing_vars, collapse = ", "))
  )
}

# Write results to JSON file
write_json(result, output_file, pretty = TRUE)

# Print success message
cat("Regression analysis completed successfully.\n")
