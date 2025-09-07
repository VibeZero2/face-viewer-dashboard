#!/usr/bin/env python3
"""
SPSS Export Script for Facial Trust Study
========================================

This script exports long format data from the facial trust study
in formats suitable for SPSS analysis, including:
- Wide format for repeated measures ANOVA
- Long format for mixed models
- Variable labels and value labels
- SPSS syntax file for data import

Usage:
    python export_spss.py [--data-dir DATA_DIR] [--output-dir OUTPUT_DIR]

Requirements:
    - pandas
    - pyreadstat (for SPSS file writing)
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

class SPSSExporter:
    """
    Exports facial trust study data in SPSS-compatible formats.
    """
    
    def __init__(self, data_dir: str = "data/responses", output_dir: str = "spss_exports"):
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
    
    def create_wide_format_for_anova(self) -> pd.DataFrame:
        """
        Create wide format data suitable for repeated measures ANOVA in SPSS.
        
        Returns:
            pd.DataFrame: Wide format data with trust ratings as separate columns
        """
        logger.info("Creating wide format for repeated measures ANOVA...")
        
        # Get trust ratings data
        trust_data = self.processor.get_question_responses('trust_rating')
        
        if trust_data.empty:
            logger.warning("No trust rating data found")
            return pd.DataFrame()
        
        # Pivot to wide format: participant_id, image_id, trust_left, trust_right, trust_full
        wide_data = trust_data.pivot_table(
            index=['participant_id', 'image_id'],
            columns='face_view',
            values='response_numeric',
            aggfunc='mean'
        ).reset_index()
        
        # Rename columns for SPSS compatibility
        wide_data.columns = ['participant_id', 'image_id', 'trust_left', 'trust_right', 'trust_full']
        
        # Add image order for analysis
        wide_data['image_order'] = range(1, len(wide_data) + 1)
        
        logger.info(f"Created wide format with {len(wide_data)} rows and {len(wide_data.columns)} columns")
        return wide_data
    
    def create_mixed_model_format(self) -> pd.DataFrame:
        """
        Create long format data suitable for mixed models in SPSS.
        
        Returns:
            pd.DataFrame: Long format data optimized for mixed models
        """
        logger.info("Creating mixed model format...")
        
        # Get all numeric responses
        numeric_data = self.processor.processed_data[
            self.processor.processed_data['is_numeric_response']
        ].copy()
        
        # Create SPSS-compatible variable names
        numeric_data['spss_question'] = numeric_data['question_type'].str.replace('_', '')
        numeric_data['spss_face_view'] = numeric_data['face_view'].str.upper()
        
        # Select relevant columns for mixed models
        mixed_data = numeric_data[[
            'participant_id', 'image_id', 'spss_face_view', 
            'spss_question', 'response_numeric', 'timestamp'
        ]].copy()
        
        # Rename for SPSS compatibility
        mixed_data.columns = [
            'PARTICIPANT_ID', 'IMAGE_ID', 'FACE_VIEW', 
            'QUESTION_TYPE', 'RESPONSE', 'TIMESTAMP'
        ]
        
        logger.info(f"Created mixed model format with {len(mixed_data)} rows")
        return mixed_data
    
    def create_variable_labels(self) -> Dict[str, str]:
        """
        Create variable labels for SPSS.
        
        Returns:
            Dict[str, str]: Variable name to label mapping
        """
        return {
            'participant_id': 'Participant ID',
            'image_id': 'Face Image ID',
            'trust_left': 'Trust Rating - Left Half',
            'trust_right': 'Trust Rating - Right Half', 
            'trust_full': 'Trust Rating - Full Face',
            'image_order': 'Image Presentation Order',
            'PARTICIPANT_ID': 'Participant ID',
            'IMAGE_ID': 'Face Image ID',
            'FACE_VIEW': 'Face View Type',
            'QUESTION_TYPE': 'Question Type',
            'RESPONSE': 'Response Value',
            'TIMESTAMP': 'Response Timestamp'
        }
    
    def create_value_labels(self) -> Dict[str, Dict]:
        """
        Create value labels for categorical variables in SPSS.
        
        Returns:
            Dict[str, Dict]: Variable name to value label mapping
        """
        return {
            'FACE_VIEW': {
                'LEFT': 'Left Half',
                'RIGHT': 'Right Half',
                'FULL': 'Full Face'
            },
            'QUESTION_TYPE': {
                'trustrating': 'Trust Rating',
                'mascchoice': 'Masculinity Choice',
                'femchoice': 'Femininity Choice',
                'emotionrating': 'Emotion Rating',
                'trustq2': 'Trust Question 2',
                'trustq3': 'Trust Question 3',
                'persq1': 'Personality Question 1',
                'persq2': 'Personality Question 2',
                'persq3': 'Personality Question 3',
                'persq4': 'Personality Question 4',
                'persq5': 'Personality Question 5'
            }
        }
    
    def generate_spss_syntax(self, wide_data: pd.DataFrame, mixed_data: pd.DataFrame) -> str:
        """
        Generate SPSS syntax for data import and analysis.
        
        Args:
            wide_data: Wide format data for ANOVA
            mixed_data: Long format data for mixed models
            
        Returns:
            str: SPSS syntax
        """
        syntax = f"""
* SPSS Syntax for Facial Trust Study Analysis
* Generated on {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}

* Set working directory
CD "{self.output_dir.absolute()}".

* Import wide format data for repeated measures ANOVA
GET DATA
  /TYPE=TXT
  /FILE="{self.output_dir / 'wide_format_anova.csv'}"
  /DELCASE=LINE
  /DELIMITERS=","
  /ARRANGEMENT=DELIMITED
  /FIRSTCASE=2
  /IMPORTCASE=ALL
  /VARIABLES=
    participant_id F8.0
    image_id A20
    trust_left F8.2
    trust_right F8.2
    trust_full F8.2
    image_order F8.0.

* Variable labels
VARIABLE LABELS
    participant_id "Participant ID"
    image_id "Face Image ID"
    trust_left "Trust Rating - Left Half"
    trust_right "Trust Rating - Right Half"
    trust_full "Trust Rating - Full Face"
    image_order "Image Presentation Order".

* Save wide format dataset
SAVE OUTFILE='wide_format_anova.sav'.

* Import long format data for mixed models
GET DATA
  /TYPE=TXT
  /FILE="{self.output_dir / 'mixed_model_format.csv'}"
  /DELCASE=LINE
  /DELIMITERS=","
  /ARRANGEMENT=DELIMITED
  /FIRSTCASE=2
  /IMPORTCASE=ALL
  /VARIABLES=
    PARTICIPANT_ID F8.0
    IMAGE_ID A20
    FACE_VIEW A10
    QUESTION_TYPE A20
    RESPONSE F8.2
    TIMESTAMP A30.

* Variable labels for long format
VARIABLE LABELS
    PARTICIPANT_ID "Participant ID"
    IMAGE_ID "Face Image ID"
    FACE_VIEW "Face View Type"
    QUESTION_TYPE "Question Type"
    RESPONSE "Response Value"
    TIMESTAMP "Response Timestamp".

* Value labels
VALUE LABELS
    FACE_VIEW
        'LEFT' 'Left Half'
        'RIGHT' 'Right Half'
        'FULL' 'Full Face'
    QUESTION_TYPE
        'trustrating' 'Trust Rating'
        'mascchoice' 'Masculinity Choice'
        'femchoice' 'Femininity Choice'
        'emotionrating' 'Emotion Rating'
        'trustq2' 'Trust Question 2'
        'trustq3' 'Trust Question 3'
        'persq1' 'Personality Question 1'
        'persq2' 'Personality Question 2'
        'persq3' 'Personality Question 3'
        'persq4' 'Personality Question 4'
        'persq5' 'Personality Question 5'.

* Save long format dataset
SAVE OUTFILE='mixed_model_format.sav'.

* Repeated Measures ANOVA Example
* (Uncomment and modify as needed)

/*
GLM trust_left trust_right trust_full
  /WSFACTOR=face_view 3 Polynomial
  /METHOD=SSTYPE(3)
  /CRITERIA=ALPHA(.05)
  /WSDESIGN=face_view
  /DESIGN=image_order.
*/

* Mixed Model Example
* (Uncomment and modify as needed)

/*
MIXED RESPONSE BY FACE_VIEW QUESTION_TYPE
  /FIXED=FACE_VIEW QUESTION_TYPE FACE_VIEW*QUESTION_TYPE
  /RANDOM=INTERCEPT | SUBJECT(PARTICIPANT_ID)
  /RANDOM=INTERCEPT | SUBJECT(IMAGE_ID)
  /METHOD=REML
  /PRINT=SOLUTION TESTCOV.
*/

* Descriptive Statistics
DESCRIPTIVES VARIABLES=trust_left trust_right trust_full
  /STATISTICS=MEAN STDDEV MIN MAX.

* Correlation Analysis
CORRELATIONS
  /VARIABLES=trust_left trust_right trust_full
  /PRINT=TWOTAIL NOSIG.

EXECUTE.
"""
        return syntax
    
    def export_all_formats(self) -> Dict[str, str]:
        """
        Export data in all SPSS-compatible formats.
        
        Returns:
            Dict[str, str]: Paths to exported files
        """
        logger.info("Starting SPSS export process...")
        
        # Load and process data
        self.load_and_process_data()
        
        # Create different data formats
        wide_data = self.create_wide_format_for_anova()
        mixed_data = self.create_mixed_model_format()
        
        exported_files = {}
        
        # Export wide format for ANOVA
        if not wide_data.empty:
            wide_path = self.output_dir / "wide_format_anova.csv"
            wide_data.to_csv(wide_path, index=False)
            exported_files['wide_format'] = str(wide_path)
            logger.info(f"Exported wide format data: {wide_path}")
        
        # Export mixed model format
        if not mixed_data.empty:
            mixed_path = self.output_dir / "mixed_model_format.csv"
            mixed_data.to_csv(mixed_path, index=False)
            exported_files['mixed_model'] = str(mixed_path)
            logger.info(f"Exported mixed model data: {mixed_path}")
        
        # Generate and save SPSS syntax
        syntax = self.generate_spss_syntax(wide_data, mixed_data)
        syntax_path = self.output_dir / "facial_trust_analysis.sps"
        with open(syntax_path, 'w', encoding='utf-8') as f:
            f.write(syntax)
        exported_files['spss_syntax'] = str(syntax_path)
        logger.info(f"Generated SPSS syntax: {syntax_path}")
        
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
        
        logger.info(f"SPSS export completed. Files saved to: {self.output_dir}")
        return exported_files

def main():
    """Main function for command line usage."""
    parser = argparse.ArgumentParser(description='Export facial trust study data for SPSS analysis')
    parser.add_argument('--data-dir', default='data/responses', 
                       help='Directory containing CSV data files')
    parser.add_argument('--output-dir', default='spss_exports',
                       help='Directory to save exported files')
    
    args = parser.parse_args()
    
    try:
        exporter = SPSSExporter(args.data_dir, args.output_dir)
        exported_files = exporter.export_all_formats()
        
        print("\n" + "="*50)
        print("SPSS EXPORT COMPLETED SUCCESSFULLY")
        print("="*50)
        print(f"Output directory: {args.output_dir}")
        print("\nExported files:")
        for file_type, file_path in exported_files.items():
            print(f"  {file_type}: {file_path}")
        print("\nNext steps:")
        print("1. Open SPSS")
        print("2. Run the generated syntax file: facial_trust_analysis.sps")
        print("3. Modify the analysis commands as needed for your research questions")
        
    except Exception as e:
        logger.error(f"Export failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
