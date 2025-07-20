"""
R Integration Module for Face Viewer Dashboard
Handles statistical analysis using R
"""
import os
import json
import csv
import datetime
import subprocess
import tempfile
from io import StringIO

class RAnalytics:
    def __init__(self, data_dir="data", r_scripts_dir="analytics/r_scripts"):
        """Initialize the R analytics module with data and scripts directories"""
        self.data_dir = data_dir
        self.r_scripts_dir = r_scripts_dir
        os.makedirs(data_dir, exist_ok=True)
        os.makedirs(r_scripts_dir, exist_ok=True)
        
    def run_analysis(self, analysis_type, data, variables=None):
        """
        Run R analysis on the provided data
        
        Parameters:
        - analysis_type: Type of analysis (e.g., 'descriptive', 'ttest', 'anova', 'correlation')
        - data: Data to analyze
        - variables: Variables to include in the analysis
        
        Returns:
        - Dictionary containing analysis results
        """
        # In a production environment with rpy2, we would directly call R
        # For our pandas-free implementation, we'll use a subprocess approach
        
        # Create a temporary CSV file with the data
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as temp_file:
            writer = csv.writer(temp_file)
            writer.writerow(data['columns'])
            for row in data['rows']:
                writer.writerow(row)
            temp_filename = temp_file.name
            
        # Generate R script based on analysis type
        r_script = self._generate_r_script(analysis_type, temp_filename, variables)
        
        # Save the R script to a temporary file
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.R') as r_file:
            r_file.write(r_script)
            r_script_filename = r_file.name
            
        # In a real environment, we would execute the R script
        # For now, we'll return mock results based on the analysis type
        results = self._generate_mock_results(analysis_type, data, variables)
        
        # Clean up temporary files
        try:
            os.unlink(temp_filename)
            os.unlink(r_script_filename)
        except:
            pass
            
        return results
        
    def _generate_r_script(self, analysis_type, data_file, variables=None):
        """Generate R script based on analysis type"""
        if variables is None:
            variables = []
            
        script = f"""
        # R script for {analysis_type} analysis
        data <- read.csv("{data_file}")
        
        """
        
        if analysis_type == 'descriptive':
            script += """
            # Descriptive statistics
            summary(data)
            """
        elif analysis_type == 'ttest':
            if len(variables) >= 2:
                script += f"""
                # T-test
                t.test(data${variables[0]}, data${variables[1]})
                """
        elif analysis_type == 'anova':
            if len(variables) >= 2:
                script += f"""
                # ANOVA
                model <- aov({variables[0]} ~ {variables[1]}, data=data)
                summary(model)
                """
        elif analysis_type == 'correlation':
            if len(variables) >= 2:
                script += f"""
                # Correlation
                cor.test(data${variables[0]}, data${variables[1]})
                """
                
        return script
        
    def _generate_mock_results(self, analysis_type, data, variables=None):
        """Generate mock results based on analysis type"""
        if variables is None:
            variables = []
            
        results = {
            'analysis_type': analysis_type,
            'timestamp': datetime.datetime.now().isoformat(),
            'variables': variables,
            'results': {}
        }
        
        if analysis_type == 'descriptive':
            results['results'] = {
                'summary': {
                    'mean': 4.2,
                    'median': 4.0,
                    'min': 1.0,
                    'max': 7.0,
                    'q1': 3.0,
                    'q3': 5.0
                }
            }
        elif analysis_type == 'ttest':
            results['results'] = {
                't_statistic': 2.45,
                'p_value': 0.018,
                'df': 98,
                'significant': True
            }
        elif analysis_type == 'anova':
            results['results'] = {
                'f_statistic': 3.78,
                'p_value': 0.025,
                'df': [2, 97],
                'significant': True
            }
        elif analysis_type == 'correlation':
            results['results'] = {
                'correlation': 0.65,
                'p_value': 0.001,
                'significant': True
            }
            
        return results
        
    def available_analyses(self):
        """Return list of available analyses"""
        return [
            {
                'id': 'descriptive',
                'name': 'Descriptive Statistics',
                'description': 'Summary statistics (mean, median, etc.)',
                'min_variables': 1,
                'max_variables': None
            },
            {
                'id': 'ttest',
                'name': 'T-Test',
                'description': 'Compare means between two groups',
                'min_variables': 2,
                'max_variables': 2
            },
            {
                'id': 'anova',
                'name': 'ANOVA',
                'description': 'Analysis of variance between groups',
                'min_variables': 2,
                'max_variables': None
            },
            {
                'id': 'correlation',
                'name': 'Correlation',
                'description': 'Measure relationship between variables',
                'min_variables': 2,
                'max_variables': 2
            },
            {
                'id': 'regression',
                'name': 'Linear Regression',
                'description': 'Predict values based on other variables',
                'min_variables': 2,
                'max_variables': None
            }
        ]
