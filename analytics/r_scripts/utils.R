#!/usr/bin/env Rscript

# Utility Functions for Face Viewer Dashboard R Scripts
# This script provides common utility functions used across R analysis scripts

# Function to validate input data
validate_data <- function(data, required_columns) {
  missing_columns <- required_columns[!required_columns %in% colnames(data)]
  if (length(missing_columns) > 0) {
    return(list(
      valid = FALSE,
      error = paste("Missing required columns:", paste(missing_columns, collapse = ", "))
    ))
  }
  
  return(list(valid = TRUE))
}

# Function to check if a variable is numeric
is_numeric_variable <- function(data, variable) {
  if (!variable %in% colnames(data)) {
    return(FALSE)
  }
  return(is.numeric(data[[variable]]))
}

# Function to format p-values for reporting
format_p_value <- function(p_value) {
  if (p_value < 0.001) {
    return("p < 0.001")
  } else if (p_value < 0.01) {
    return(paste0("p = ", format(round(p_value, 3), nsmall = 3)))
  } else if (p_value < 0.05) {
    return(paste0("p = ", format(round(p_value, 3), nsmall = 3)))
  } else {
    return(paste0("p = ", format(round(p_value, 3), nsmall = 3)))
  }
}

# Function to interpret correlation strength
interpret_correlation <- function(r) {
  if (abs(r) < 0.3) {
    strength <- "weak"
  } else if (abs(r) < 0.7) {
    strength <- "moderate"
  } else {
    strength <- "strong"
  }
  
  direction <- if (r > 0) "positive" else "negative"
  
  return(list(
    strength = strength,
    direction = direction
  ))
}

# Function to create a basic data summary
summarize_data <- function(data) {
  summary_list <- list()
  
  # Get basic info
  summary_list$rows <- nrow(data)
  summary_list$columns <- ncol(data)
  summary_list$column_names <- colnames(data)
  
  # Summarize each column
  column_summaries <- list()
  for (col in colnames(data)) {
    col_data <- data[[col]]
    
    if (is.numeric(col_data)) {
      # Numeric column
      column_summaries[[col]] <- list(
        type = "numeric",
        mean = mean(col_data, na.rm = TRUE),
        median = median(col_data, na.rm = TRUE),
        sd = sd(col_data, na.rm = TRUE),
        min = min(col_data, na.rm = TRUE),
        max = max(col_data, na.rm = TRUE),
        missing = sum(is.na(col_data))
      )
    } else {
      # Categorical column
      freq_table <- table(col_data)
      column_summaries[[col]] <- list(
        type = "categorical",
        unique_values = length(unique(col_data)),
        frequencies = as.list(freq_table),
        mode = names(freq_table)[which.max(freq_table)],
        missing = sum(is.na(col_data))
      )
    }
  }
  
  summary_list$columns_summary <- column_summaries
  return(summary_list)
}
