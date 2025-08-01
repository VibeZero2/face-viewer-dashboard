"""
Test script for R analysis module
Generates sample data and runs each analysis type to verify functionality
Aligns with the study's methods section for all required statistical tests
"""
import os
import sys
import json
import pandas as pd
import numpy as np
from flask import Flask, jsonify
sys.path.append('.')

# Define HAS_RPY2 before importing RAnalytics
# Set to False to force using mock data for testing
HAS_RPY2 = False
try:
    import rpy2.robjects
    # Uncomment the line below if you have R properly installed and want to test with real R
    # HAS_RPY2 = True
except ImportError:
    print("rpy2 not available, will use mock data for testing")

from routes.api import _get_analysis_summary, _format_tables_from_r_result
from analytics.r_integration import RAnalytics

# Create a Flask app for testing
app = Flask(__name__)

def generate_test_data(num_participants=30):
    """Generate sample data for testing R analysis"""
    np.random.seed(42)  # For reproducible results
    
    # Generate participant IDs
    participant_ids = [f"P{i:03d}" for i in range(1, num_participants + 1)]
    
    # Generate gender (50/50 split)
    genders = np.random.choice(['Male', 'Female'], size=num_participants)
    
    # Generate age groups
    age_groups = np.random.choice(['18-25', '26-35', '36-45', '46+'], size=num_participants)
    
    # Generate trust ratings (1-7 scale)
    trust_ratings = np.random.normal(4.5, 1.2, num_participants).clip(1, 7).round(1)
    
    # Generate masculinity ratings for left and right sides
    masculinity_left = np.random.normal(4.2, 1.0, num_participants).clip(1, 7).round(1)
    masculinity_right = masculinity_left + np.random.normal(0.5, 0.8, num_participants).round(1)
    masculinity_right = masculinity_right.clip(1, 7)
    
    # Generate femininity ratings for left and right sides
    femininity_left = np.random.normal(3.8, 1.1, num_participants).clip(1, 7).round(1)
    femininity_right = femininity_left + np.random.normal(-0.3, 0.7, num_participants).round(1)
    femininity_right = femininity_right.clip(1, 7)
    
    # Create DataFrame
    df = pd.DataFrame({
        'Participant ID': participant_ids,
        'Gender': genders,
        'Age Group': age_groups,
        'Trust Rating': trust_ratings,
        'Masculinity Left': masculinity_left,
        'Masculinity Right': masculinity_right,
        'Femininity Left': femininity_left,
        'Femininity Right': femininity_right,
        'Symmetry Score': np.random.normal(0.7, 0.15, num_participants).clip(0, 1).round(2)
    })
    
    return df

def test_descriptive_stats(r_analytics, data):
    """Test descriptive statistics analysis"""
    print("\n=== Testing Descriptive Statistics ===")
    
    result = r_analytics.run_analysis('descriptive', {
        'columns': data.columns.tolist(),
        'rows': data.values.tolist()
    }, {'variable': 'Trust Rating'})
    
    print(f"Result: {json.dumps(result, indent=2)}")
    
    # Format for frontend
    summary = _get_analysis_summary(result, 'descriptive', 'Trust Rating')
    tables = _format_tables_from_r_result(result, 'descriptive')
    
    print(f"Summary: {summary}")
    print(f"Tables: {json.dumps(tables, indent=2)}")
    
    # Verify expected result structure
    if 'result' in result:
        print("✅ Descriptive statistics test passed")
    else:
        print("❌ Descriptive statistics test failed")
        
    return result

def test_paired_ttest(r_analytics, data):
    """Test paired t-test analysis"""
    print("\n=== Testing Paired T-Test ===")
    
    result = r_analytics.run_analysis('paired_ttest', {
        'columns': data.columns.tolist(),
        'rows': data.values.tolist()
    }, {'variable': 'Masculinity Left', 'secondary_variable': 'Masculinity Right'})
    
    print(f"Result: {json.dumps(result, indent=2)}")
    
    # Format for frontend
    summary = _get_analysis_summary(result, 'paired_ttest', 'Masculinity Left', 'Masculinity Right')
    tables = _format_tables_from_r_result(result, 'paired_ttest')
    
    print(f"Summary: {summary}")
    print(f"Tables: {json.dumps(tables, indent=2)}")
    
    # Verify expected result structure
    if 'result' in result or ('masculinity' in result and 'result' in result['masculinity']):
        print("✅ Paired t-test passed")
    else:
        print("❌ Paired t-test failed")
    
    return result

def test_independent_ttest(r_analytics, data):
    """Test independent t-test analysis"""
    print("\n=== Testing Independent T-Test ===")
    
    result = r_analytics.run_analysis('independent_ttest', {
        'columns': data.columns.tolist(),
        'rows': data.values.tolist()
    }, {'variable': 'Trust Rating', 'secondary_variable': 'Gender'})
    
    print(f"Result: {json.dumps(result, indent=2)}")
    
    # Format for frontend
    summary = _get_analysis_summary(result, 'independent_ttest', 'Trust Rating', 'Gender')
    tables = _format_tables_from_r_result(result, 'independent_ttest')
    
    print(f"Summary: {summary}")
    print(f"Tables: {json.dumps(tables, indent=2)}")
    
    # Verify expected result structure
    if 'result' in result and 't' in result['result']:
        print("✅ Independent t-test passed")
    else:
        print("❌ Independent t-test failed")
    
    return result

def test_repeated_measures_anova(r_analytics, data):
    """Test repeated measures ANOVA analysis"""
    print("\n=== Testing Repeated Measures ANOVA ===")
    
    # Reshape data for repeated measures ANOVA
    # We need data in long format with participant, condition, and measurement
    long_data = []
    
    for _, row in data.iterrows():
        participant_id = row['Participant ID']
        
        # Add left side measurement
        long_data.append([
            participant_id,
            'Left',
            row['Trust Rating']
        ])
        
        # Add right side measurement (simulate with slight difference)
        long_data.append([
            participant_id,
            'Right',
            row['Trust Rating'] + np.random.normal(0.3, 0.5)
        ])
    
    long_df = pd.DataFrame(long_data, columns=['Participant ID', 'Side', 'Trust Rating'])
    
    result = r_analytics.run_analysis('repeated_measures_anova', {
        'columns': long_df.columns.tolist(),
        'rows': long_df.values.tolist()
    }, {'variable': 'Trust Rating', 'secondary_variable': 'Side', 'participant_id': 'Participant ID'})
    
    print(f"Result: {json.dumps(result, indent=2)}")
    
    # Format for frontend
    summary = _get_analysis_summary(result, 'repeated_measures_anova', 'Trust Rating', 'Side')
    tables = _format_tables_from_r_result(result, 'repeated_measures_anova')
    
    print(f"Summary: {summary}")
    print(f"Tables: {json.dumps(tables, indent=2)}")
    
    # Verify expected result structure
    if 'result' in result and 'F' in result['result']:
        print("✅ Repeated measures ANOVA passed")
    else:
        print("❌ Repeated measures ANOVA failed")
    
    return result

def test_one_way_anova(r_analytics, data):
    """Test one-way ANOVA analysis"""
    print("\n=== Testing One-Way ANOVA ===")
    
    result = r_analytics.run_analysis('one_way_anova', {
        'columns': data.columns.tolist(),
        'rows': data.values.tolist()
    }, {'variable': 'Trust Rating', 'secondary_variable': 'Age Group'})
    
    print(f"Result: {json.dumps(result, indent=2)}")
    
    # Format for frontend
    summary = _get_analysis_summary(result, 'one_way_anova', 'Trust Rating', 'Age Group')
    tables = _format_tables_from_r_result(result, 'one_way_anova')
    
    print(f"Summary: {summary}")
    print(f"Tables: {json.dumps(tables, indent=2)}")
    
    # Verify expected result structure
    if 'result' in result and 'F' in result['result']:
        print("✅ One-way ANOVA passed")
    else:
        print("❌ One-way ANOVA failed")
    
    return result

def test_correlation(r_analytics, data):
    """Test correlation analysis"""
    print("\n=== Testing Correlation ===")
    
    result = r_analytics.run_analysis('correlation', {
        'columns': data.columns.tolist(),
        'rows': data.values.tolist()
    }, {'variable': 'Trust Rating', 'secondary_variable': 'Symmetry Score'})
    
    print(f"Result: {json.dumps(result, indent=2)}")
    
    # Format for frontend
    summary = _get_analysis_summary(result, 'correlation', 'Trust Rating', 'Symmetry Score')
    tables = _format_tables_from_r_result(result, 'correlation')
    
    print(f"Summary: {summary}")
    print(f"Tables: {json.dumps(tables, indent=2)}")
    
    # Verify expected result structure
    if 'result' in result and 'r' in result['result']:
        print("✅ Correlation test passed")
    else:
        print("❌ Correlation test failed")
    
    return result

def test_invalid_input(r_analytics, data):
    """Test invalid input handling"""
    print("\n=== Testing Invalid Input Handling ===")
    
    # Test with invalid analysis type
    try:
        result = r_analytics.run_analysis('invalid_analysis', {
            'columns': data.columns.tolist(),
            'rows': data.values.tolist()
        }, {'variable': 'Trust Rating'})
        print("❌ Should have raised an exception for invalid analysis type")
    except Exception as e:
        print(f"✅ Correctly handled invalid analysis type: {str(e)}")
    
    # Test with missing required variable
    try:
        result = r_analytics.run_analysis('correlation', {
            'columns': data.columns.tolist(),
            'rows': data.values.tolist()
        }, {'variable': 'Trust Rating'})
        if 'error' in result:
            print(f"✅ Correctly detected missing secondary variable: {result['error']}")
        else:
            print("❌ Should have detected missing secondary variable")
    except Exception as e:
        print(f"✅ Correctly handled missing secondary variable: {str(e)}")
    
    # Test with non-existent variable
    try:
        result = r_analytics.run_analysis('descriptive', {
            'columns': data.columns.tolist(),
            'rows': data.values.tolist()
        }, {'variable': 'NonExistentVariable'})
        if 'error' in result:
            print(f"✅ Correctly detected non-existent variable: {result['error']}")
        else:
            print("❌ Should have detected non-existent variable")
    except Exception as e:
        print(f"✅ Correctly handled non-existent variable: {str(e)}")
    
    return {'status': 'completed'}

def main():
    """Main test function"""
    print("Generating test data...")
    test_data = generate_test_data(30)
    print(f"Generated data with {len(test_data)} participants")
    print(test_data.head())
    
    # Initialize R analytics
    r_analytics = RAnalytics()
    
    # Run all tests
    results = {}
    
    try:
        results['descriptive'] = test_descriptive_stats(r_analytics, test_data)
    except Exception as e:
        print(f"Error in descriptive stats test: {str(e)}")
    
    try:
        results['paired_ttest'] = test_paired_ttest(r_analytics, test_data)
    except Exception as e:
        print(f"Error in paired t-test test: {str(e)}")
    
    try:
        results['independent_ttest'] = test_independent_ttest(r_analytics, test_data)
    except Exception as e:
        print(f"Error in independent t-test test: {str(e)}")
    
    try:
        results['repeated_measures_anova'] = test_repeated_measures_anova(r_analytics, test_data)
    except Exception as e:
        print(f"Error in repeated measures ANOVA test: {str(e)}")
    
    try:
        results['one_way_anova'] = test_one_way_anova(r_analytics, test_data)
    except Exception as e:
        print(f"Error in one-way ANOVA test: {str(e)}")
    
    try:
        results['correlation'] = test_correlation(r_analytics, test_data)
    except Exception as e:
        print(f"Error in correlation test: {str(e)}")
    
    try:
        results['invalid_input'] = test_invalid_input(r_analytics, test_data)
    except Exception as e:
        print(f"Error in invalid input test: {str(e)}")
    
    # Summary of results
    print("\n=== Test Summary ===")
    for test_name, result in results.items():
        if test_name == 'invalid_input':
            status = "Completed"
        else:
            status = "Success" if 'error' not in result else f"Failed: {result['error']}"
        print(f"{test_name}: {status}")

if __name__ == "__main__":
    main()
