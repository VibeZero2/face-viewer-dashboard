#!/usr/bin/env python3
"""
Pilot Analysis Script for Facial Trust Study
===========================================

This script performs pilot statistical analyses on the facial trust study data,
including:
- Repeated measures ANOVA
- Intraclass correlation (ICC)
- Effect sizes
- Basic descriptive statistics

Usage:
    python pilot_analysis.py [--data-dir DATA_DIR] [--output-dir OUTPUT_DIR]

Requirements:
    - pandas
    - numpy
    - scipy
    - scikit-learn (for ICC calculation)
"""

import argparse
import pandas as pd
import numpy as np
from pathlib import Path
import logging
from typing import Dict, List, Tuple, Optional
import sys
import os
from scipy import stats
from scipy.stats import f_oneway, ttest_rel
import warnings
warnings.filterwarnings('ignore')

# Add the analysis directory to the path
sys.path.append(str(Path(__file__).parent / "analysis"))
from long_format_processor import LongFormatProcessor

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class PilotAnalyzer:
    """
    Performs pilot statistical analyses on facial trust study data.
    """
    
    def __init__(self, data_dir: str = "data/responses", output_dir: str = "pilot_analysis"):
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
    
    def calculate_descriptive_statistics(self) -> Dict:
        """
        Calculate descriptive statistics for trust ratings.
        
        Returns:
            Dict: Descriptive statistics
        """
        logger.info("Calculating descriptive statistics...")
        
        # Get trust ratings data
        trust_data = self.processor.get_question_responses('trust_rating')
        
        if trust_data.empty:
            logger.warning("No trust rating data found")
            return {}
        
        # Group by face view
        desc_stats = {}
        for face_view in ['left', 'right', 'full']:
            view_data = trust_data[trust_data['face_view'] == face_view]['response_numeric'].dropna()
            
            if len(view_data) > 0:
                desc_stats[face_view] = {
                    'n': len(view_data),
                    'mean': view_data.mean(),
                    'std': view_data.std(),
                    'median': view_data.median(),
                    'min': view_data.min(),
                    'max': view_data.max(),
                    'q25': view_data.quantile(0.25),
                    'q75': view_data.quantile(0.75),
                    'skewness': stats.skew(view_data),
                    'kurtosis': stats.kurtosis(view_data)
                }
        
        # Overall statistics
        all_trust = trust_data['response_numeric'].dropna()
        desc_stats['overall'] = {
            'n': len(all_trust),
            'mean': all_trust.mean(),
            'std': all_trust.std(),
            'median': all_trust.median(),
            'min': all_trust.min(),
            'max': all_trust.max(),
            'q25': all_trust.quantile(0.25),
            'q75': all_trust.quantile(0.75),
            'skewness': stats.skew(all_trust),
            'kurtosis': stats.kurtosis(all_trust)
        }
        
        return desc_stats
    
    def calculate_correlations(self) -> Dict:
        """
        Calculate correlations between face views.
        
        Returns:
            Dict: Correlation results
        """
        logger.info("Calculating correlations...")
        
        # Get wide format trust data
        wide_trust = self.processor.get_trust_ratings_by_view()
        
        if wide_trust.empty:
            logger.warning("No wide format trust data found")
            return {}
        
        # Calculate correlations
        correlations = {}
        
        # Pearson correlations
        if 'left' in wide_trust.columns and 'right' in wide_trust.columns:
            left_right = wide_trust[['left', 'right']].dropna()
            if len(left_right) > 0:
                corr, p_value = stats.pearsonr(left_right['left'], left_right['right'])
                correlations['left_right'] = {'correlation': corr, 'p_value': p_value, 'n': len(left_right)}
        
        if 'left' in wide_trust.columns and 'full' in wide_trust.columns:
            left_full = wide_trust[['left', 'full']].dropna()
            if len(left_full) > 0:
                corr, p_value = stats.pearsonr(left_full['left'], left_full['full'])
                correlations['left_full'] = {'correlation': corr, 'p_value': p_value, 'n': len(left_full)}
        
        if 'right' in wide_trust.columns and 'full' in wide_trust.columns:
            right_full = wide_trust[['right', 'full']].dropna()
            if len(right_full) > 0:
                corr, p_value = stats.pearsonr(right_full['right'], right_full['full'])
                correlations['right_full'] = {'correlation': corr, 'p_value': p_value, 'n': len(right_full)}
        
        return correlations
    
    def repeated_measures_anova(self) -> Dict:
        """
        Perform repeated measures ANOVA on trust ratings.
        
        Returns:
            Dict: ANOVA results
        """
        logger.info("Performing repeated measures ANOVA...")
        
        # Get wide format trust data
        wide_trust = self.processor.get_trust_ratings_by_view()
        
        if wide_trust.empty:
            logger.warning("No wide format trust data found for ANOVA")
            return {}
        
        # Prepare data for ANOVA - need to ensure all arrays have the same length
        anova_data = []
        face_views = []
        
        # Find the minimum length among all face view columns
        min_length = float('inf')
        for face_view in ['left', 'right', 'full']:
            if face_view in wide_trust.columns:
                view_data = wide_trust[face_view].dropna()
                if len(view_data) > 0:
                    min_length = min(min_length, len(view_data))
        
        if min_length == float('inf') or min_length < 2:
            logger.warning("Insufficient data for ANOVA")
            return {}
        
        # Truncate all arrays to the same length
        for face_view in ['left', 'right', 'full']:
            if face_view in wide_trust.columns:
                view_data = wide_trust[face_view].dropna()
                if len(view_data) >= min_length:
                    # Take the first min_length values to ensure equal sample sizes
                    truncated_data = view_data.iloc[:min_length]
                    anova_data.append(truncated_data)
                    face_views.append(face_view)
        
        if len(anova_data) < 2:
            logger.warning("Insufficient data for ANOVA after truncation")
            return {}
        
        # Perform one-way ANOVA
        f_stat, p_value = f_oneway(*anova_data)
        
        # Calculate effect size (eta squared)
        # Get all data for effect size calculation
        all_data = []
        for data in anova_data:
            all_data.extend(data)
        
        ss_between = 0
        ss_total = 0
        grand_mean = np.mean(all_data)
        
        for data in anova_data:
            group_mean = np.mean(data)
            ss_between += len(data) * (group_mean - grand_mean) ** 2
            for value in data:
                ss_total += (value - grand_mean) ** 2
        
        eta_squared = ss_between / ss_total if ss_total > 0 else 0
        
        # Post-hoc pairwise t-tests
        pairwise_tests = {}
        if len(anova_data) >= 2:
            for i in range(len(anova_data)):
                for j in range(i + 1, len(anova_data)):
                    try:
                        t_stat, p_val = ttest_rel(anova_data[i], anova_data[j])
                        pairwise_tests[f"{face_views[i]}_vs_{face_views[j]}"] = {
                            't_statistic': t_stat,
                            'p_value': p_val,
                            'n': len(anova_data[i])
                        }
                    except Exception as e:
                        logger.warning(f"Could not perform t-test for {face_views[i]} vs {face_views[j]}: {e}")
                        pairwise_tests[f"{face_views[i]}_vs_{face_views[j]}"] = {
                            't_statistic': np.nan,
                            'p_value': np.nan,
                            'n': len(anova_data[i])
                        }
        
        return {
            'f_statistic': f_stat,
            'p_value': p_value,
            'eta_squared': eta_squared,
            'face_views': face_views,
            'group_means': [np.mean(data) for data in anova_data],
            'group_stds': [np.std(data) for data in anova_data],
            'group_ns': [len(data) for data in anova_data],
            'pairwise_tests': pairwise_tests
        }
    
    def calculate_icc(self) -> Dict:
        """
        Calculate Intraclass Correlation Coefficient (ICC).
        
        Returns:
            Dict: ICC results
        """
        logger.info("Calculating Intraclass Correlation Coefficient...")
        
        # Get wide format trust data
        wide_trust = self.processor.get_trust_ratings_by_view()
        
        if wide_trust.empty:
            logger.warning("No wide format trust data found for ICC")
            return {}
        
        # Prepare data for ICC calculation
        icc_data = []
        for face_view in ['left', 'right', 'full']:
            if face_view in wide_trust.columns:
                icc_data.append(wide_trust[face_view].dropna())
        
        if len(icc_data) < 2:
            logger.warning("Insufficient data for ICC calculation")
            return {}
        
        # Create matrix for ICC calculation
        max_length = max(len(data) for data in icc_data)
        icc_matrix = np.full((max_length, len(icc_data)), np.nan)
        
        for i, data in enumerate(icc_data):
            icc_matrix[:len(data), i] = data
        
        # Calculate ICC using variance components
        # ICC(2,1) - two-way random effects, single measure
        try:
            # Calculate variance components
            n_subjects = icc_matrix.shape[0]
            n_raters = icc_matrix.shape[1]
            
            # Mean of all observations
            grand_mean = np.nanmean(icc_matrix)
            
            # Between-subjects variance (MSB)
            subject_means = np.nanmean(icc_matrix, axis=1)
            msb = np.nanvar(subject_means) * n_raters
            
            # Between-raters variance (MSR)
            rater_means = np.nanmean(icc_matrix, axis=0)
            msr = np.nanvar(rater_means) * n_subjects
            
            # Error variance (MSE)
            mse = 0
            for i in range(n_subjects):
                for j in range(n_raters):
                    if not np.isnan(icc_matrix[i, j]):
                        mse += (icc_matrix[i, j] - subject_means[i] - rater_means[j] + grand_mean) ** 2
            
            mse = mse / ((n_subjects - 1) * (n_raters - 1))
            
            # ICC calculation
            icc_2_1 = (msb - mse) / (msb + (n_raters - 1) * mse)
            
            # ICC(2,k) - two-way random effects, average measure
            icc_2_k = (msb - mse) / msb
            
            return {
                'icc_2_1': icc_2_1,
                'icc_2_k': icc_2_k,
                'msb': msb,
                'msr': msr,
                'mse': mse,
                'n_subjects': n_subjects,
                'n_raters': n_raters
            }
            
        except Exception as e:
            logger.error(f"Error calculating ICC: {e}")
            return {}
    
    def calculate_effect_sizes(self) -> Dict:
        """
        Calculate effect sizes (Cohen's d) for pairwise comparisons.
        
        Returns:
            Dict: Effect size results
        """
        logger.info("Calculating effect sizes...")
        
        # Get wide format trust data
        wide_trust = self.processor.get_trust_ratings_by_view()
        
        if wide_trust.empty:
            logger.warning("No wide format trust data found for effect sizes")
            return {}
        
        effect_sizes = {}
        
        # Calculate Cohen's d for pairwise comparisons
        def cohens_d(x, y):
            """Calculate Cohen's d for paired samples."""
            n = len(x)
            diff = x - y
            mean_diff = np.mean(diff)
            std_diff = np.std(diff, ddof=1)
            return mean_diff / std_diff if std_diff > 0 else 0
        
        # Left vs Right
        if 'left' in wide_trust.columns and 'right' in wide_trust.columns:
            left_right = wide_trust[['left', 'right']].dropna()
            if len(left_right) > 0:
                d = cohens_d(left_right['left'], left_right['right'])
                effect_sizes['left_vs_right'] = {'cohens_d': d, 'n': len(left_right)}
        
        # Left vs Full
        if 'left' in wide_trust.columns and 'full' in wide_trust.columns:
            left_full = wide_trust[['left', 'full']].dropna()
            if len(left_full) > 0:
                d = cohens_d(left_full['left'], left_full['full'])
                effect_sizes['left_vs_full'] = {'cohens_d': d, 'n': len(left_full)}
        
        # Right vs Full
        if 'right' in wide_trust.columns and 'full' in wide_trust.columns:
            right_full = wide_trust[['right', 'full']].dropna()
            if len(right_full) > 0:
                d = cohens_d(right_full['right'], right_full['full'])
                effect_sizes['right_vs_full'] = {'cohens_d': d, 'n': len(right_full)}
        
        return effect_sizes
    
    def run_pilot_analysis(self) -> Dict:
        """
        Run all pilot analyses.
        
        Returns:
            Dict: All analysis results
        """
        logger.info("Starting pilot analysis...")
        
        # Load and process data
        self.load_and_process_data()
        
        # Run all analyses
        results = {
            'descriptive_statistics': self.calculate_descriptive_statistics(),
            'correlations': self.calculate_correlations(),
            'repeated_measures_anova': self.repeated_measures_anova(),
            'icc': self.calculate_icc(),
            'effect_sizes': self.calculate_effect_sizes(),
            'data_summary': self.processor.get_data_summary()
        }
        
        return results
    
    def save_results(self, results: Dict) -> str:
        """
        Save analysis results to files.
        
        Args:
            results: Analysis results dictionary
            
        Returns:
            str: Path to results file
        """
        logger.info("Saving analysis results...")
        
        # Create detailed results report
        report_path = self.output_dir / "pilot_analysis_report.txt"
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write("FACIAL TRUST STUDY - PILOT ANALYSIS REPORT\n")
            f.write("=" * 50 + "\n\n")
            f.write(f"Generated on: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            # Data summary
            f.write("DATA SUMMARY\n")
            f.write("-" * 20 + "\n")
            data_summary = results.get('data_summary', {})
            for key, value in data_summary.items():
                f.write(f"{key}: {value}\n")
            f.write("\n")
            
            # Descriptive statistics
            f.write("DESCRIPTIVE STATISTICS\n")
            f.write("-" * 25 + "\n")
            desc_stats = results.get('descriptive_statistics', {})
            for face_view, stats_dict in desc_stats.items():
                f.write(f"\n{face_view.upper()}:\n")
                for stat, value in stats_dict.items():
                    f.write(f"  {stat}: {value:.3f}\n")
            f.write("\n")
            
            # Correlations
            f.write("CORRELATIONS\n")
            f.write("-" * 15 + "\n")
            correlations = results.get('correlations', {})
            for comparison, corr_data in correlations.items():
                f.write(f"{comparison}: r = {corr_data['correlation']:.3f}, p = {corr_data['p_value']:.3f}, n = {corr_data['n']}\n")
            f.write("\n")
            
            # Repeated measures ANOVA
            f.write("REPEATED MEASURES ANOVA\n")
            f.write("-" * 25 + "\n")
            anova_results = results.get('repeated_measures_anova', {})
            if anova_results:
                f.write(f"F-statistic: {anova_results['f_statistic']:.3f}\n")
                f.write(f"p-value: {anova_results['p_value']:.3f}\n")
                f.write(f"Eta-squared: {anova_results['eta_squared']:.3f}\n")
                f.write(f"Face views: {anova_results['face_views']}\n")
                f.write(f"Group means: {[f'{m:.3f}' for m in anova_results['group_means']]}\n")
                f.write(f"Group stds: {[f'{s:.3f}' for s in anova_results['group_stds']]}\n")
                f.write(f"Group ns: {anova_results['group_ns']}\n")
                
                # Pairwise tests
                f.write("\nPairwise t-tests:\n")
                for comparison, test_data in anova_results.get('pairwise_tests', {}).items():
                    f.write(f"  {comparison}: t = {test_data['t_statistic']:.3f}, p = {test_data['p_value']:.3f}\n")
            f.write("\n")
            
            # ICC
            f.write("INTRACLASS CORRELATION (ICC)\n")
            f.write("-" * 30 + "\n")
            icc_results = results.get('icc', {})
            if icc_results:
                f.write(f"ICC(2,1): {icc_results['icc_2_1']:.3f}\n")
                f.write(f"ICC(2,k): {icc_results['icc_2_k']:.3f}\n")
                f.write(f"n_subjects: {icc_results['n_subjects']}\n")
                f.write(f"n_raters: {icc_results['n_raters']}\n")
            f.write("\n")
            
            # Effect sizes
            f.write("EFFECT SIZES (COHEN'S D)\n")
            f.write("-" * 25 + "\n")
            effect_sizes = results.get('effect_sizes', {})
            for comparison, effect_data in effect_sizes.items():
                f.write(f"{comparison}: d = {effect_data['cohens_d']:.3f}, n = {effect_data['n']}\n")
            f.write("\n")
            
            # Interpretation
            f.write("INTERPRETATION\n")
            f.write("-" * 15 + "\n")
            f.write("Effect size guidelines (Cohen's d):\n")
            f.write("  Small: 0.2\n")
            f.write("  Medium: 0.5\n")
            f.write("  Large: 0.8\n\n")
            f.write("ICC interpretation:\n")
            f.write("  < 0.5: Poor reliability\n")
            f.write("  0.5-0.75: Moderate reliability\n")
            f.write("  0.75-0.9: Good reliability\n")
            f.write("  > 0.9: Excellent reliability\n")
        
        logger.info(f"Results saved to: {report_path}")
        return str(report_path)

def main():
    """Main function for command line usage."""
    parser = argparse.ArgumentParser(description='Run pilot analysis on facial trust study data')
    parser.add_argument('--data-dir', default='data/responses', 
                       help='Directory containing CSV data files')
    parser.add_argument('--output-dir', default='pilot_analysis',
                       help='Directory to save analysis results')
    
    args = parser.parse_args()
    
    try:
        analyzer = PilotAnalyzer(args.data_dir, args.output_dir)
        results = analyzer.run_pilot_analysis()
        report_path = analyzer.save_results(results)
        
        print("\n" + "="*50)
        print("PILOT ANALYSIS COMPLETED SUCCESSFULLY")
        print("="*50)
        print(f"Results saved to: {report_path}")
        print(f"Output directory: {args.output_dir}")
        
        # Print summary to console
        print("\nQUICK SUMMARY:")
        print("-" * 20)
        
        # Data summary
        data_summary = results.get('data_summary', {})
        print(f"Total responses: {data_summary.get('total_responses', 'N/A')}")
        print(f"Unique participants: {data_summary.get('unique_participants', 'N/A')}")
        print(f"Unique images: {data_summary.get('unique_images', 'N/A')}")
        
        # ANOVA results
        anova_results = results.get('repeated_measures_anova', {})
        if anova_results:
            print(f"ANOVA F-statistic: {anova_results['f_statistic']:.3f}")
            print(f"ANOVA p-value: {anova_results['p_value']:.3f}")
            print(f"Effect size (η²): {anova_results['eta_squared']:.3f}")
        
        # ICC results
        icc_results = results.get('icc', {})
        if icc_results:
            print(f"ICC(2,1): {icc_results['icc_2_1']:.3f}")
            print(f"ICC(2,k): {icc_results['icc_2_k']:.3f}")
        
        print(f"\nDetailed results available in: {report_path}")
        
    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
