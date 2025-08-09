"""
Statistical analysis utilities for Face Viewer Dashboard
"""
import os
import logging
import numpy as np
from typing import Dict, Any, List, Optional, Tuple, Union
from scipy import stats

# Import utilities
from utils.csv_loader import load_csv_files, filter_data

# Set up logging
log = logging.getLogger(__name__)

def calculate_descriptive_stats(data: List[Dict[str, Any]], variable: str) -> Dict[str, Any]:
    """
    Calculate descriptive statistics for a variable
    
    Args:
        data: List of data dictionaries
        variable: Variable to analyze
        
    Returns:
        Dictionary of descriptive statistics
    """
    # Extract values, ignoring missing or non-numeric
    values = []
    for row in data:
        if variable in row and row[variable]:
            try:
                value = float(row[variable])
                values.append(value)
            except (ValueError, TypeError):
                pass
    
    if not values:
        return {
            'n': 0,
            'mean': None,
            'median': None,
            'std': None,
            'min': None,
            'max': None,
            'q1': None,
            'q3': None
        }
    
    # Calculate statistics
    values_array = np.array(values)
    return {
        'n': len(values),
        'mean': float(np.mean(values_array)),
        'median': float(np.median(values_array)),
        'std': float(np.std(values_array, ddof=1)),
        'min': float(np.min(values_array)),
        'max': float(np.max(values_array)),
        'q1': float(np.percentile(values_array, 25)),
        'q3': float(np.percentile(values_array, 75))
    }

def run_ttest(data: List[Dict[str, Any]], variable: str) -> Dict[str, Any]:
    """
    Run a paired t-test comparing left vs right face ratings
    
    Args:
        data: List of data dictionaries
        variable: Variable to analyze
        
    Returns:
        Dictionary of t-test results
    """
    # Group data by participant and face_id
    grouped_data = {}
    for row in data:
        if (
            'participant_id' in row and 
            'face_id' in row and 
            'face_version' in row and 
            variable in row and 
            row[variable]
        ):
            key = (row['participant_id'], row['face_id'])
            if key not in grouped_data:
                grouped_data[key] = {}
                
            try:
                value = float(row[variable])
                face_version = row['face_version'].lower()
                
                if 'left' in face_version:
                    grouped_data[key]['left'] = value
                elif 'right' in face_version:
                    grouped_data[key]['right'] = value
            except (ValueError, TypeError):
                pass
    
    # Extract paired samples
    left_values = []
    right_values = []
    
    for key, values in grouped_data.items():
        if 'left' in values and 'right' in values:
            left_values.append(values['left'])
            right_values.append(values['right'])
    
    if len(left_values) < 2:
        return {
            'error': 'Insufficient paired data for t-test',
            'n_pairs': len(left_values)
        }
    
    # Run paired t-test
    t_stat, p_value = stats.ttest_rel(left_values, right_values)
    
    # Calculate effect size (Cohen's d for paired samples)
    diff = np.array(left_values) - np.array(right_values)
    effect_size = np.mean(diff) / np.std(diff, ddof=1)
    
    return {
        'n_pairs': len(left_values),
        'left_mean': float(np.mean(left_values)),
        'right_mean': float(np.mean(right_values)),
        'left_std': float(np.std(left_values, ddof=1)),
        'right_std': float(np.std(right_values, ddof=1)),
        't_stat': float(t_stat),
        'p_value': float(p_value),
        'effect_size': float(effect_size),
        'significant': p_value < 0.05,
        'mean_diff': float(np.mean(left_values) - np.mean(right_values))
    }

def run_wilcoxon(data: List[Dict[str, Any]], variable: str) -> Dict[str, Any]:
    """
    Run a Wilcoxon signed-rank test comparing left vs right face ratings
    
    Args:
        data: List of data dictionaries
        variable: Variable to analyze
        
    Returns:
        Dictionary of Wilcoxon test results
    """
    # Group data by participant and face_id
    grouped_data = {}
    for row in data:
        if (
            'participant_id' in row and 
            'face_id' in row and 
            'face_version' in row and 
            variable in row and 
            row[variable]
        ):
            key = (row['participant_id'], row['face_id'])
            if key not in grouped_data:
                grouped_data[key] = {}
                
            try:
                value = float(row[variable])
                face_version = row['face_version'].lower()
                
                if 'left' in face_version:
                    grouped_data[key]['left'] = value
                elif 'right' in face_version:
                    grouped_data[key]['right'] = value
            except (ValueError, TypeError):
                pass
    
    # Extract paired samples
    left_values = []
    right_values = []
    
    for key, values in grouped_data.items():
        if 'left' in values and 'right' in values:
            left_values.append(values['left'])
            right_values.append(values['right'])
    
    if len(left_values) < 5:  # Wilcoxon test needs at least 5 pairs
        return {
            'error': 'Insufficient paired data for Wilcoxon test (need at least 5 pairs)',
            'n_pairs': len(left_values)
        }
    
    # Run Wilcoxon signed-rank test
    stat, p_value = stats.wilcoxon(left_values, right_values)
    
    # Calculate effect size (r = Z / sqrt(N))
    # For Wilcoxon, we need to calculate Z from the p-value
    z_score = stats.norm.ppf(1 - p_value / 2)
    effect_size = z_score / np.sqrt(len(left_values) * 2)
    
    return {
        'n_pairs': len(left_values),
        'left_median': float(np.median(left_values)),
        'right_median': float(np.median(right_values)),
        'stat': float(stat),
        'p_value': float(p_value),
        'z_score': float(z_score),
        'effect_size': float(effect_size),
        'significant': p_value < 0.05
    }

def run_correlation(data: List[Dict[str, Any]], variable1: str, variable2: str) -> Dict[str, Any]:
    """
    Run a correlation analysis between two variables
    
    Args:
        data: List of data dictionaries
        variable1: First variable
        variable2: Second variable
        
    Returns:
        Dictionary of correlation results
    """
    # Extract paired values
    pairs = []
    for row in data:
        if variable1 in row and variable2 in row and row[variable1] and row[variable2]:
            try:
                val1 = float(row[variable1])
                val2 = float(row[variable2])
                pairs.append((val1, val2))
            except (ValueError, TypeError):
                pass
    
    if len(pairs) < 3:
        return {
            'error': 'Insufficient data for correlation analysis',
            'n': len(pairs)
        }
    
    # Split into separate arrays
    x = np.array([p[0] for p in pairs])
    y = np.array([p[1] for p in pairs])
    
    # Calculate Pearson correlation
    pearson_r, pearson_p = stats.pearsonr(x, y)
    
    # Calculate Spearman correlation
    spearman_r, spearman_p = stats.spearmanr(x, y)
    
    return {
        'n': len(pairs),
        'pearson_r': float(pearson_r),
        'pearson_p': float(pearson_p),
        'spearman_r': float(spearman_r),
        'spearman_p': float(spearman_p),
        'significant_pearson': pearson_p < 0.05,
        'significant_spearman': spearman_p < 0.05
    }

def format_apa_results(test_type: str, results: Dict[str, Any], variable: str, secondary_variable: str = None) -> str:
    """
    Format analysis results in APA style
    
    Args:
        test_type: Type of test ('descriptives', 'ttest', 'wilcoxon', 'correlation')
        results: Dictionary of test results
        variable: Primary variable analyzed
        secondary_variable: Secondary variable (for correlation)
        
    Returns:
        APA-formatted results string
    """
    if 'error' in results:
        return f"Error: {results['error']}"
    
    if test_type == 'descriptives':
        return (
            f"Descriptive statistics for {variable} (N = {results['n']}): "
            f"M = {results['mean']:.2f}, SD = {results['std']:.2f}, "
            f"Median = {results['median']:.2f}, Range = {results['min']:.1f}-{results['max']:.1f}"
        )
    
    elif test_type == 'ttest':
        sig_text = "significant" if results['significant'] else "not significant"
        return (
            f"A paired-samples t-test revealed a {sig_text} difference between {variable} ratings "
            f"for left face (M = {results['left_mean']:.2f}, SD = {results['left_std']:.2f}) and "
            f"right face (M = {results['right_mean']:.2f}, SD = {results['right_std']:.2f}), "
            f"t({results['n_pairs'] - 1}) = {abs(results['t_stat']):.2f}, p = {results['p_value']:.3f}, "
            f"d = {abs(results['effect_size']):.2f}."
        )
    
    elif test_type == 'wilcoxon':
        sig_text = "significant" if results['significant'] else "not significant"
        return (
            f"A Wilcoxon signed-rank test indicated a {sig_text} difference in {variable} ratings "
            f"between left face (Mdn = {results['left_median']:.2f}) and "
            f"right face (Mdn = {results['right_median']:.2f}), "
            f"Z = {abs(results['z_score']):.2f}, p = {results['p_value']:.3f}, r = {abs(results['effect_size']):.2f}."
        )
    
    elif test_type == 'correlation':
        pearson_sig = "significant" if results['significant_pearson'] else "not significant"
        return (
            f"A Pearson correlation analysis revealed a {pearson_sig} relationship between "
            f"{variable} and {secondary_variable}, r({results['n'] - 2}) = {results['pearson_r']:.2f}, "
            f"p = {results['pearson_p']:.3f}. "
            f"A Spearman rank correlation yielded rs = {results['spearman_r']:.2f}, p = {results['spearman_p']:.3f}."
        )
    
    return f"Analysis of {variable} using {test_type} was completed successfully."

def run_analysis(
    test_type: str, 
    variable: str, 
    filters: Dict[str, Any] = None, 
    secondary_variable: str = None
) -> Dict[str, Any]:
    """
    Run the specified analysis on the data
    
    Args:
        test_type: Type of test ('descriptives', 'ttest', 'wilcoxon', 'correlation')
        variable: Variable to analyze
        filters: Filters to apply to the data
        secondary_variable: Secondary variable (for correlation)
        
    Returns:
        Dictionary with analysis results and APA-formatted text
    """
    try:
        # Load and filter data
        data = load_csv_files()
        if filters:
            data = filter_data(data, filters)
        
        if not data:
            return {
                'ok': False,
                'error': 'No data found matching the specified filters',
                'apa': 'Error: No data found matching the specified filters.'
            }
        
        # Run the appropriate analysis
        if test_type == 'descriptives':
            results = calculate_descriptive_stats(data, variable)
        elif test_type == 'ttest':
            results = run_ttest(data, variable)
        elif test_type == 'wilcoxon':
            results = run_wilcoxon(data, variable)
        elif test_type == 'correlation' and secondary_variable:
            results = run_correlation(data, variable, secondary_variable)
        else:
            return {
                'ok': False,
                'error': f'Unsupported analysis type: {test_type}',
                'apa': f'Error: Unsupported analysis type: {test_type}'
            }
        
        # Format results in APA style
        apa_text = format_apa_results(test_type, results, variable, secondary_variable)
        
        return {
            'ok': True,
            'test': test_type,
            'variable': variable,
            'secondary_variable': secondary_variable,
            'results': results,
            'apa': apa_text
        }
        
    except Exception as e:
        log.error(f"Error in run_analysis: {str(e)}", exc_info=True)
        return {
            'ok': False,
            'error': str(e),
            'apa': f'Error: An unexpected error occurred: {str(e)}'
        }
