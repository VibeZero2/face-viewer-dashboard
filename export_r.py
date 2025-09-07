#!/usr/bin/env python3
"""
R Export Script for Facial Trust Study
=====================================

This script exports long format data from the facial trust study
in formats suitable for R analysis, including:
- R data files (.rds format)
- CSV files with proper formatting
- R script with analysis examples
- Package installation and setup

Usage:
    python export_r.py [--data-dir DATA_DIR] [--output-dir OUTPUT_DIR]

Requirements:
    - pandas
    - rpy2 (optional, for direct R integration)
"""

import argparse
import pandas as pd
import numpy as np
from pathlib import Path
import logging
from typing import Dict, List, Tuple
import sys
import os

# Add the analysis directory to the path
sys.path.append(str(Path(__file__).parent / "analysis"))
from long_format_processor import LongFormatProcessor

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class RExporter:
    """
    Exports facial trust study data in R-compatible formats.
    """
    
    def __init__(self, data_dir: str = "data/responses", output_dir: str = "r_exports"):
        self.data_dir = Path(data_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Initialize data processor
        self.processor = LongFormatProcessor(str(self.data_dir), test_mode=False)
        
    def load_and_process_data(self):
        """Load and process the long format data."""
        logger.info("Loading and processing long format data...")
        self.processor.load_data()
        self.processor.process_data()
        logger.info("Data processing completed.")
    
    def create_analysis_datasets(self) -> Dict[str, pd.DataFrame]:
        """
        Create different datasets optimized for various R analyses.
        
        Returns:
            Dict[str, pd.DataFrame]: Different analysis datasets
        """
        logger.info("Creating analysis datasets...")
        
        datasets = {}
        
        # 1. Full long format data
        datasets['long_format'] = self.processor.processed_data.copy()
        
        # 2. Trust ratings only (for main analysis)
        trust_data = self.processor.get_question_responses('trust_rating')
        if not trust_data.empty:
            datasets['trust_ratings'] = trust_data.copy()
        
        # 3. Wide format for repeated measures
        if not trust_data.empty:
            wide_trust = trust_data.pivot_table(
                index=['participant_id', 'image_id'],
                columns='face_view',
                values='response_numeric',
                aggfunc='mean'
            ).reset_index()
            wide_trust.columns = ['participant_id', 'image_id', 'trust_left', 'trust_right', 'trust_full']
            datasets['wide_trust'] = wide_trust
        
        # 4. Numeric responses only
        numeric_data = self.processor.processed_data[
            self.processor.processed_data['is_numeric_response']
        ].copy()
        datasets['numeric_responses'] = numeric_data
        
        # 5. Participant-level summary
        participant_summary = self.processor.processed_data.groupby('participant_id').agg({
            'response_numeric': ['count', 'mean', 'std'],
            'image_id': 'nunique',
            'question_type': lambda x: x.nunique()
        }).round(3)
        participant_summary.columns = ['total_responses', 'mean_response', 'response_std', 'unique_images', 'question_types']
        participant_summary = participant_summary.reset_index()
        datasets['participant_summary'] = participant_summary
        
        # 6. Image-level summary
        image_summary = self.processor.get_image_summary()
        if not image_summary.empty:
            datasets['image_summary'] = image_summary
        
        logger.info(f"Created {len(datasets)} analysis datasets")
        return datasets
    
    def generate_r_script(self, datasets: Dict[str, pd.DataFrame]) -> str:
        """
        Generate R script with analysis examples.
        
        Args:
            datasets: Dictionary of analysis datasets
            
        Returns:
            str: R script content
        """
        script = f"""
# R Analysis Script for Facial Trust Study
# Generated on {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}

# Load required packages
required_packages <- c("tidyverse", "lme4", "lmerTest", "car", "psych", 
                      "ggplot2", "dplyr", "reshape2", "corrplot", "ICC")

# Install packages if not already installed
new_packages <- required_packages[!(required_packages %in% installed.packages()[,"Package"])]
if(length(new_packages)) install.packages(new_packages)

# Load packages
library(tidyverse)
library(lme4)
library(lmerTest)
library(car)
library(psych)
library(ggplot2)
library(dplyr)
library(reshape2)
library(corrplot)
library(ICC)

# Set working directory
setwd("{self.output_dir.absolute()}")

# Load data
cat("Loading facial trust study data...\\n")

# Load long format data
long_data <- read.csv("long_format_data.csv", stringsAsFactors = FALSE)
long_data$timestamp <- as.POSIXct(long_data$timestamp)
long_data$participant_id <- as.factor(long_data$participant_id)
long_data$image_id <- as.factor(long_data$image_id)
long_data$face_view <- as.factor(long_data$face_view)
long_data$question_type <- as.factor(long_data$question_type)

# Load wide format trust data
wide_trust <- read.csv("wide_trust_data.csv", stringsAsFactors = FALSE)
wide_trust$participant_id <- as.factor(wide_trust$participant_id)
wide_trust$image_id <- as.factor(wide_trust$image_id)

# Load participant summary
participant_summary <- read.csv("participant_summary.csv", stringsAsFactors = FALSE)
participant_summary$participant_id <- as.factor(participant_summary$participant_id)

# Load image summary
image_summary <- read.csv("image_summary.csv", stringsAsFactors = FALSE)
image_summary$image_id <- as.factor(image_summary$image_id)

cat("Data loaded successfully.\\n")
cat("Long format data:", nrow(long_data), "rows\\n")
cat("Wide trust data:", nrow(wide_trust), "rows\\n")
cat("Participants:", length(unique(long_data$participant_id)), "\\n")
cat("Images:", length(unique(long_data$image_id)), "\\n")

# =============================================================================
# DESCRIPTIVE STATISTICS
# =============================================================================

cat("\\n=== DESCRIPTIVE STATISTICS ===\\n")

# Overall descriptive statistics
describe(wide_trust[c("trust_left", "trust_right", "trust_full")])

# Descriptive statistics by face view
trust_long <- long_data %>% 
  filter(question_type == "trust_rating") %>%
  select(participant_id, image_id, face_view, response_numeric)

describeBy(trust_long$response_numeric, trust_long$face_view)

# Participant-level statistics
cat("\\nParticipant-level summary:\\n")
summary(participant_summary)

# =============================================================================
# CORRELATION ANALYSIS
# =============================================================================

cat("\\n=== CORRELATION ANALYSIS ===\\n")

# Correlations between face views
trust_correlations <- cor(wide_trust[c("trust_left", "trust_right", "trust_full")], 
                         use = "complete.obs")
print(trust_correlations)

# Correlation plot
corrplot(trust_correlations, method = "circle", type = "upper", 
         addCoef.col = "black", number.cex = 0.8)

# =============================================================================
# REPEATED MEASURES ANOVA
# =============================================================================

cat("\\n=== REPEATED MEASURES ANOVA ===\\n")

# Prepare data for repeated measures ANOVA
rm_data <- wide_trust %>%
  select(participant_id, trust_left, trust_right, trust_full) %>%
  pivot_longer(cols = c(trust_left, trust_right, trust_full),
               names_to = "face_view",
               values_to = "trust_rating") %>%
  mutate(face_view = factor(face_view, levels = c("trust_left", "trust_right", "trust_full")))

# Repeated measures ANOVA
rm_anova <- aov(trust_rating ~ face_view + Error(participant_id/face_view), data = rm_data)
summary(rm_anova)

# Post-hoc comparisons
pairwise.t.test(rm_data$trust_rating, rm_data$face_view, 
                paired = TRUE, p.adjust.method = "bonferroni")

# =============================================================================
# MIXED EFFECTS MODELS
# =============================================================================

cat("\\n=== MIXED EFFECTS MODELS ===\\n")

# Prepare data for mixed models
mixed_data <- long_data %>%
  filter(question_type == "trust_rating") %>%
  select(participant_id, image_id, face_view, response_numeric) %>%
  mutate(face_view = factor(face_view, levels = c("left", "right", "full")))

# Mixed model with random intercepts for participants and images
mixed_model <- lmer(response_numeric ~ face_view + (1|participant_id) + (1|image_id), 
                    data = mixed_data)
summary(mixed_model)

# Model with random slopes
mixed_model_slopes <- lmer(response_numeric ~ face_view + (1 + face_view|participant_id) + (1|image_id), 
                           data = mixed_data)
summary(mixed_model_slopes)

# Model comparison
anova(mixed_model, mixed_model_slopes)

# =============================================================================
# INTRACLASS CORRELATION (ICC)
# =============================================================================

cat("\\n=== INTRACLASS CORRELATION ===\\n")

# ICC for trust ratings across face views
icc_data <- wide_trust %>%
  select(trust_left, trust_right, trust_full) %>%
  as.matrix()

# ICC calculation
icc_result <- ICC(icc_data)
print(icc_result)

# =============================================================================
# VISUALIZATIONS
# =============================================================================

cat("\\n=== CREATING VISUALIZATIONS ===\\n")

# Box plot of trust ratings by face view
ggplot(trust_long, aes(x = face_view, y = response_numeric, fill = face_view)) +
  geom_boxplot() +
  geom_jitter(width = 0.2, alpha = 0.5) +
  labs(title = "Trust Ratings by Face View",
       x = "Face View",
       y = "Trust Rating",
       fill = "Face View") +
  theme_minimal()

ggsave("trust_ratings_boxplot.png", width = 10, height = 6, dpi = 300)

# Violin plot
ggplot(trust_long, aes(x = face_view, y = response_numeric, fill = face_view)) +
  geom_violin() +
  geom_boxplot(width = 0.1, fill = "white") +
  labs(title = "Distribution of Trust Ratings by Face View",
       x = "Face View",
       y = "Trust Rating") +
  theme_minimal()

ggsave("trust_ratings_violin.png", width = 10, height = 6, dpi = 300)

# Scatter plot matrix
pairs(wide_trust[c("trust_left", "trust_right", "trust_full")], 
      main = "Scatter Plot Matrix: Trust Ratings")

# Individual differences plot
participant_means <- trust_long %>%
  group_by(participant_id, face_view) %>%
  summarise(mean_trust = mean(response_numeric, na.rm = TRUE), .groups = "drop")

ggplot(participant_means, aes(x = face_view, y = mean_trust, group = participant_id)) +
  geom_line(alpha = 0.3) +
  geom_point(alpha = 0.5) +
  stat_summary(aes(group = 1), fun = mean, geom = "line", 
               color = "red", size = 1.5) +
  stat_summary(aes(group = 1), fun = mean, geom = "point", 
               color = "red", size = 3) +
  labs(title = "Individual Differences in Trust Ratings",
       x = "Face View",
       y = "Mean Trust Rating") +
  theme_minimal()

ggsave("individual_differences.png", width = 10, height = 6, dpi = 300)

# =============================================================================
# EFFECT SIZES
# =============================================================================

cat("\\n=== EFFECT SIZES ===\\n")

# Cohen's d for pairwise comparisons
library(effsize)

# Left vs Right
left_right <- cohen.d(wide_trust$trust_left, wide_trust$trust_right, paired = TRUE)
cat("Cohen's d (Left vs Right):", left_right$estimate, "\\n")

# Left vs Full
left_full <- cohen.d(wide_trust$trust_left, wide_trust$trust_full, paired = TRUE)
cat("Cohen's d (Left vs Full):", left_full$estimate, "\\n")

# Right vs Full
right_full <- cohen.d(wide_trust$trust_right, wide_trust$trust_full, paired = TRUE)
cat("Cohen's d (Right vs Full):", right_full$estimate, "\\n")

# =============================================================================
# SAVE RESULTS
# =============================================================================

cat("\\n=== SAVING RESULTS ===\\n")

# Save model results
sink("analysis_results.txt")
cat("Facial Trust Study - Analysis Results\\n")
cat("=====================================\\n\\n")

cat("Repeated Measures ANOVA:\\n")
print(summary(rm_anova))
cat("\\n\\n")

cat("Mixed Effects Model:\\n")
print(summary(mixed_model))
cat("\\n\\n")

cat("ICC Results:\\n")
print(icc_result)
cat("\\n\\n")

cat("Effect Sizes:\\n")
cat("Cohen's d (Left vs Right):", left_right$estimate, "\\n")
cat("Cohen's d (Left vs Full):", left_full$estimate, "\\n")
cat("Cohen's d (Right vs Full):", right_full$estimate, "\\n")

sink()

cat("Analysis completed successfully!\\n")
cat("Results saved to analysis_results.txt\\n")
cat("Plots saved as PNG files\\n")
"""
        return script
    
    def export_all_formats(self) -> Dict[str, str]:
        """
        Export data in all R-compatible formats.
        
        Returns:
            Dict[str, str]: Paths to exported files
        """
        logger.info("Starting R export process...")
        
        # Load and process data
        self.load_and_process_data()
        
        # Create analysis datasets
        datasets = self.create_analysis_datasets()
        
        exported_files = {}
        
        # Export each dataset as CSV
        for dataset_name, dataset in datasets.items():
            if not dataset.empty:
                csv_path = self.output_dir / f"{dataset_name}_data.csv"
                dataset.to_csv(csv_path, index=False)
                exported_files[dataset_name] = str(csv_path)
                logger.info(f"Exported {dataset_name} dataset: {csv_path}")
        
        # Generate and save R script
        r_script = self.generate_r_script(datasets)
        script_path = self.output_dir / "facial_trust_analysis.R"
        with open(script_path, 'w', encoding='utf-8') as f:
            f.write(r_script)
        exported_files['r_script'] = str(script_path)
        logger.info(f"Generated R script: {script_path}")
        
        # Create data summary
        summary = self.processor.get_data_summary()
        summary_path = self.output_dir / "data_summary.txt"
        with open(summary_path, 'w', encoding='utf-8') as f:
            f.write("Facial Trust Study - Data Summary\n")
            f.write("=" * 40 + "\n\n")
            for key, value in summary.items():
                f.write(f"{key}: {value}\n")
        exported_files['summary'] = str(summary_path)
        logger.info(f"Created data summary: {summary_path}")
        
        # Create README for R analysis
        readme_content = f"""
# Facial Trust Study - R Analysis Package

This package contains data and scripts for analyzing the facial trust study data in R.

## Files Included

- `long_format_data.csv` - Full long format data
- `trust_ratings_data.csv` - Trust ratings only
- `wide_trust_data.csv` - Wide format trust data for repeated measures
- `numeric_responses_data.csv` - All numeric responses
- `participant_summary_data.csv` - Participant-level summary
- `image_summary_data.csv` - Image-level summary
- `facial_trust_analysis.R` - Complete analysis script
- `data_summary.txt` - Data summary statistics

## Quick Start

1. Open R or RStudio
2. Set working directory to this folder
3. Run: `source("facial_trust_analysis.R")`

## Required R Packages

The analysis script will automatically install these packages if needed:
- tidyverse
- lme4
- lmerTest
- car
- psych
- ggplot2
- dplyr
- reshape2
- corrplot
- ICC
- effsize

## Analysis Includes

- Descriptive statistics
- Correlation analysis
- Repeated measures ANOVA
- Mixed effects models
- Intraclass correlation (ICC)
- Effect sizes (Cohen's d)
- Data visualizations

## Output Files

After running the analysis, you'll get:
- `analysis_results.txt` - Statistical results
- `trust_ratings_boxplot.png` - Box plot visualization
- `trust_ratings_violin.png` - Violin plot visualization
- `individual_differences.png` - Individual differences plot

Generated on: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        
        readme_path = self.output_dir / "README.md"
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(readme_content)
        exported_files['readme'] = str(readme_path)
        logger.info(f"Created README: {readme_path}")
        
        logger.info(f"R export completed. Files saved to: {self.output_dir}")
        return exported_files

def main():
    """Main function for command line usage."""
    parser = argparse.ArgumentParser(description='Export facial trust study data for R analysis')
    parser.add_argument('--data-dir', default='data/responses', 
                       help='Directory containing CSV data files')
    parser.add_argument('--output-dir', default='r_exports',
                       help='Directory to save exported files')
    
    args = parser.parse_args()
    
    try:
        exporter = RExporter(args.data_dir, args.output_dir)
        exported_files = exporter.export_all_formats()
        
        print("\n" + "="*50)
        print("R EXPORT COMPLETED SUCCESSFULLY")
        print("="*50)
        print(f"Output directory: {args.output_dir}")
        print("\nExported files:")
        for file_type, file_path in exported_files.items():
            print(f"  {file_type}: {file_path}")
        print("\nNext steps:")
        print("1. Open R or RStudio")
        print("2. Set working directory to the output folder")
        print("3. Run: source('facial_trust_analysis.R')")
        print("4. Check the generated plots and results")
        
    except Exception as e:
        logger.error(f"Export failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
