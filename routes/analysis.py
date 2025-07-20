"""
R Analysis routes for Face Viewer Dashboard
Handles R statistical analysis requests
"""

from flask import Blueprint, request, jsonify, send_file
import os
import pandas as pd
import tempfile
import json
from utils.export_history import log_export

# Create blueprint
analysis_bp = Blueprint('analysis', __name__)

@analysis_bp.route('/run_analysis', methods=['POST'])
def run_analysis():
    """
    Run R analysis on data
    
    Expected form data:
    - test: Type of test to run (anova, ttest, corr)
    - dv: Dependent variable
    - iv: Independent variable
    - additional parameters based on test type
    
    Returns:
        JSON response with analysis results
    """
    try:
        # Get form data
        test = request.form.get('test')
        dv = request.form.get('dv')
        iv = request.form.get('iv')
        
        # Validate required parameters
        if not all([test, dv, iv]):
            return jsonify({
                'success': False,
                'error': 'Missing required parameters'
            }), 400
        
        # Import rpy2 here to avoid dependency issues if R is not installed
        try:
            from rpy2 import robjects as ro
            from rpy2.robjects import pandas2ri
            pandas2ri.activate()
        except ImportError:
            return jsonify({
                'success': False,
                'error': 'R integration is not available. Please install rpy2 and R.'
            }), 500
        
        # Path to data file
        data_path = os.path.join(os.getcwd(), 'data', 'working_data.csv')
        
        # Check if data file exists
        if not os.path.exists(data_path):
            return jsonify({
                'success': False,
                'error': 'Data file not found'
            }), 404
        
        # Load data
        data_df = pd.read_csv(data_path)
        
        # Create temporary file for results
        output_file = os.path.join(os.getcwd(), 'exports', 'analysis_out.csv')
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        # Set R variables
        ro.r.assign('dv', dv)
        ro.r.assign('iv', iv)
        ro.r.assign('data_path', data_path)
        ro.r.assign('output_path', output_file)
        
        # Run R analysis based on test type
        if test == 'anova':
            r_script = '''
                df <- read.csv(data_path)
                res <- summary(aov(as.formula(paste(dv, "~", iv)), data=df))
                capture.output(res, file=output_path)
                # Also create a JSON summary
                json_result <- list(
                    test = "ANOVA",
                    dv = dv,
                    iv = iv,
                    df_residuals = res[[1]]$Df[2],
                    df_between = res[[1]]$Df[1],
                    f_value = res[[1]]$"F value"[1],
                    p_value = res[[1]]$"Pr(>F)"[1],
                    significant = res[[1]]$"Pr(>F)"[1] < 0.05
                )
                writeLines(jsonlite::toJSON(json_result), paste0(output_path, ".json"))
            '''
        elif test == 'ttest':
            r_script = '''
                df <- read.csv(data_path)
                res <- t.test(df[[dv]] ~ df[[iv]])
                capture.output(res, file=output_path)
                # Also create a JSON summary
                json_result <- list(
                    test = "t-test",
                    dv = dv,
                    iv = iv,
                    t_value = res$statistic,
                    df = res$parameter,
                    p_value = res$p.value,
                    significant = res$p.value < 0.05,
                    mean_diff = diff(res$estimate)
                )
                writeLines(jsonlite::toJSON(json_result), paste0(output_path, ".json"))
            '''
        elif test == 'corr':
            r_script = '''
                df <- read.csv(data_path)
                res <- cor.test(df[[dv]], df[[iv]])
                capture.output(res, file=output_path)
                # Also create a JSON summary
                json_result <- list(
                    test = "Correlation",
                    var1 = dv,
                    var2 = iv,
                    correlation = res$estimate,
                    t_value = res$statistic,
                    df = res$parameter,
                    p_value = res$p.value,
                    significant = res$p.value < 0.05
                )
                writeLines(jsonlite::toJSON(json_result), paste0(output_path, ".json"))
            '''
        else:
            return jsonify({
                'success': False,
                'error': f'Unknown test type: {test}'
            }), 400
        
        # Execute R script
        ro.r(r_script)
        
        # Read results
        with open(output_file, 'r') as f:
            results_text = f.read()
        
        # Read JSON results if available
        json_results = {}
        json_path = output_file + '.json'
        if os.path.exists(json_path):
            with open(json_path, 'r') as f:
                json_results = json.load(f)
        
        # Log export
        filter_desc = f"Test: {test}, DV: {dv}, IV: {iv}"
        log_export('r_analysis', len(data_df), filter_desc)
        
        # Return results
        return jsonify({
            'success': True,
            'results': results_text,
            'json_results': json_results,
            'test': test,
            'dv': dv,
            'iv': iv
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
