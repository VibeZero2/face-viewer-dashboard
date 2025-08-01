"""
R Integration Module for Face Viewer Dashboard
Handles statistical analysis using R via rpy2
"""
import os
import json
import csv
import datetime
import subprocess
import tempfile
from io import StringIO

# Global flag to force mock mode (useful for testing)
FORCE_MOCK_MODE = False

# Check if R_HOME is set before attempting to import rpy2
if not FORCE_MOCK_MODE and os.environ.get('R_HOME'):
    # Import rpy2 modules
    try:
        import rpy2.robjects as robjects
        from rpy2.robjects import pandas2ri
        from rpy2.robjects.packages import importr
        from rpy2.robjects.conversion import localconverter
        HAS_RPY2 = True
    except ImportError:
        HAS_RPY2 = False
        print("Warning: rpy2 not available, falling back to mock data")
else:
    HAS_RPY2 = False
    if FORCE_MOCK_MODE:
        print("Mock mode forced, using mock data")
    else:
        print("Warning: R_HOME not set, falling back to mock data")

class RAnalytics:
    def __init__(self, data_dir="data", r_scripts_dir="analytics/r_scripts", force_mock=False):
        """
        Initialize the R analytics module with data and scripts directories
        
        Parameters:
        - data_dir: Directory for data files
        - r_scripts_dir: Directory for R scripts
        - force_mock: Force mock mode even if rpy2 is available
        """
        self.data_dir = data_dir
        self.r_scripts_dir = r_scripts_dir
        self.force_mock = force_mock
        
        # Create directories if they don't exist
        os.makedirs(data_dir, exist_ok=True)
        os.makedirs(r_scripts_dir, exist_ok=True)
        
        # Set instance-level flag for using mock data
        self.use_mock = force_mock or not HAS_RPY2
        
        # Initialize R environment if rpy2 is available and not forcing mock mode
        if HAS_RPY2 and not force_mock:
            try:
                # Import necessary R packages
                self.base = importr('base')
                self.stats = importr('stats')
                self.utils = importr('utils')
                
                # Try to import tidyverse if available
                try:
                    self.tidyverse = importr('tidyverse')
                except:
                    print("Warning: tidyverse not available in R")
                    
                print("R environment initialized successfully")
            except Exception as e:
                print(f"Error initializing R environment: {str(e)}")
                # Set instance-level flag to use mock data
                self.use_mock = True
        
    def run_analysis(self, analysis_type, data, variables=None):
        """
        Run R analysis on the provided data
        
        Parameters:
        - analysis_type: Type of analysis (e.g., 'descriptive', 'paired_ttest', 'independent_ttest', etc.)
        - data: Data to analyze (dict with 'columns' and 'rows')
        - variables: Variables to include in the analysis (dict with 'variable' and optional 'secondary_variable')
        
        Returns:
        - Dictionary containing analysis results
        """
        # Validate inputs
        if not data or 'columns' not in data or 'rows' not in data:
            return {
                'error': 'Invalid data format',
                'message': 'Data must contain columns and rows',
                'status': 'error'
            }
            
        if not data['rows']:
            return {
                'error': 'Empty dataset',
                'message': 'No data rows provided for analysis',
                'status': 'error'
            }
            
        # Log analysis request
        print(f"Running {analysis_type} analysis with variables: {variables}")
        print(f"Data has {len(data['columns'])} columns and {len(data['rows'])} rows")
        
        # Check if we should use mock data (either forced or rpy2 not available)
        if self.use_mock:
            print(f"Using mock data for {analysis_type} analysis")
            return self._generate_mock_results(analysis_type, data, variables)
            
        # If rpy2 is available and not forcing mock mode, use it for direct R integration
        if HAS_RPY2 and not self.force_mock:
            try:
                return self._run_analysis_with_rpy2(analysis_type, data, variables)
            except Exception as e:
                print(f"Error running R analysis: {str(e)}")
                # Fall back to mock results if R analysis fails
                return {
                    'error': str(e),
                    'message': 'R analysis failed, falling back to mock results',
                    'status': 'warning',
                    'result': self._generate_mock_results(analysis_type, data, variables)['result']
                }
        else:
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
                
            # Return mock results since we can't execute R without rpy2
            results = self._generate_mock_results(analysis_type, data, variables)
            
            # Clean up temporary files
            try:
                os.unlink(temp_filename)
                os.unlink(r_script_filename)
            except:
                pass
                
            return results
            
    def _run_analysis_with_rpy2(self, analysis_type, data, variables=None):
        """
        Run R analysis using rpy2 direct integration
        """
        if variables is None:
            variables = []
            
        # Convert data to R dataframe
        r_data = self._convert_data_to_r_dataframe(data)
        
        # Run the appropriate analysis based on type
        if analysis_type == 'repeated_measures_anova':
            return self._run_repeated_measures_anova(r_data, variables)
        elif analysis_type == 'paired_ttest':
            return self._run_paired_ttest(r_data, variables)
        elif analysis_type == 'independent_ttest':
            return self._run_independent_ttest(r_data, variables)
        elif analysis_type == 'correlation':
            return self._run_correlation(r_data, variables)
        elif analysis_type == 'one_way_anova':
            return self._run_one_way_anova(r_data, variables)
        elif analysis_type == 'descriptive':
            return self._run_descriptive_stats(r_data, variables)
        else:
            return {
                'error': 'Invalid analysis type',
                'message': f'Analysis type {analysis_type} not supported',
                'status': 'error'
            }
            
    def _convert_data_to_r_dataframe(self, data):
        """
        Convert Python data dict to R dataframe
        """
        # Create a temporary CSV file with the data
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as temp_file:
            writer = csv.writer(temp_file)
            writer.writerow(data['columns'])
            for row in data['rows']:
                writer.writerow(row)
            temp_filename = temp_file.name
            
        # Read the CSV file into an R dataframe
        r_read_csv = robjects.r['read.csv']
        r_data = r_read_csv(temp_filename)
        
        # Clean up temporary file
        try:
            os.unlink(temp_filename)
        except:
            pass
            
        return r_data
        
    def _run_repeated_measures_anova(self, r_data, variables):
        """
        Run repeated measures ANOVA to test if participants rate different face sides (left/right) 
        with significantly different trust levels
        
        Expected variables: ['participant', 'side', 'trust']
        """
        try:
            # Check if required variables exist in the dataframe
            if not all(var in r_data.names for var in ['participant', 'side', 'trust']):
                return {
                    'error': 'Missing required variables',
                    'message': 'Repeated measures ANOVA requires participant, side, and trust variables',
                    'status': 'error'
                }
                
            # Convert participant and side to factors
            robjects.r('''
            run_repeated_anova <- function(df) {
              df$participant <- as.factor(df$participant)
              df$side <- as.factor(df$side)
              model <- aov(trust ~ side + Error(participant/side), data = df)
              result <- summary(model)
              
              # Extract F-value, p-value, and degrees of freedom
              within_result <- result[[2]][[1]]
              f_value <- within_result$`F value`[1]
              p_value <- within_result$`Pr(>F)`[1]
              df1 <- within_result$Df[1]
              df2 <- within_result$Df[2]
              
              # Calculate effect size (partial eta-squared)
              ss_effect <- within_result$`Sum Sq`[1]
              ss_error <- within_result$`Sum Sq`[2]
              effect_size <- ss_effect / (ss_effect + ss_error)
              
              # Create result list
              list(
                f_value = f_value,
                p_value = p_value,
                df1 = df1,
                df2 = df2,
                effect_size = effect_size,
                significant = p_value < 0.05
              )
            }
            ''')
            
            # Run the analysis
            run_repeated_anova = robjects.r['run_repeated_anova']
            result = run_repeated_anova(r_data)
            
            # Convert R result to Python dict
            py_result = {
                'test': 'Repeated Measures ANOVA',
                'result': {
                    'F': result.rx2('f_value')[0],
                    'p': result.rx2('p_value')[0],
                    'df1': int(result.rx2('df1')[0]),
                    'df2': int(result.rx2('df2')[0]),
                    'effect_size': result.rx2('effect_size')[0],
                    'significant': bool(result.rx2('significant')[0]),
                    'interpretation': 'Significant difference in trust ratings between face sides.' 
                                      if bool(result.rx2('significant')[0]) else 
                                      'No significant difference in trust ratings between face sides.'
                }
            }
            
            return py_result
            
        except Exception as e:
            return {
                'error': str(e),
                'message': 'Error running repeated measures ANOVA',
                'status': 'error'
            }
            
    def _run_paired_ttest(self, r_data, variables):
        """
        Run paired t-tests to compare masculinity and femininity ratings between left and right sides
        
        Expected variables: ['masculinity_left', 'masculinity_right'] or ['femininity_left', 'femininity_right']
        """
        try:
            # Check if we have masculinity or femininity variables
            has_masc = all(var in r_data.names for var in ['masculinity_left', 'masculinity_right'])
            has_fem = all(var in r_data.names for var in ['femininity_left', 'femininity_right'])
            
            if not (has_masc or has_fem):
                return {
                    'error': 'Missing required variables',
                    'message': 'Paired t-test requires either masculinity_left/masculinity_right or femininity_left/femininity_right variables',
                    'status': 'error'
                }
                
            # Define R function for paired t-test
            robjects.r('''
            run_paired_ttest <- function(df, var_type) {
              if (var_type == "masculinity") {
                test <- t.test(df$masculinity_left, df$masculinity_right, paired = TRUE)
              } else {
                test <- t.test(df$femininity_left, df$femininity_right, paired = TRUE)
              }
              
              # Calculate effect size (Cohen's d)
              if (var_type == "masculinity") {
                mean_diff <- mean(df$masculinity_left - df$masculinity_right, na.rm = TRUE)
                sd_diff <- sd(df$masculinity_left - df$masculinity_right, na.rm = TRUE)
              } else {
                mean_diff <- mean(df$femininity_left - df$femininity_right, na.rm = TRUE)
                sd_diff <- sd(df$femininity_left - df$femininity_right, na.rm = TRUE)
              }
              
              n <- length(df[,1])
              d <- mean_diff / sd_diff
              
              # Create result list
              list(
                t_value = test$statistic,
                p_value = test$p.value,
                df = test$parameter,
                mean_diff = mean_diff,
                effect_size = d,
                significant = test$p.value < 0.05
              )
            }
            ''')
            
            results = {}
            run_paired_ttest = robjects.r['run_paired_ttest']
            
            # Run masculinity test if variables exist
            if has_masc:
                masc_result = run_paired_ttest(r_data, robjects.StrVector(['masculinity']))
                results['masculinity'] = {
                    'test': 'Paired t-test (Masculinity)',
                    'result': {
                        't': masc_result.rx2('t_value')[0],
                        'p': masc_result.rx2('p_value')[0],
                        'df': int(masc_result.rx2('df')[0]),
                        'mean_diff': masc_result.rx2('mean_diff')[0],
                        'effect_size': masc_result.rx2('effect_size')[0],
                        'significant': bool(masc_result.rx2('significant')[0]),
                        'interpretation': 'Significant difference in masculinity ratings between face sides.' 
                                          if bool(masc_result.rx2('significant')[0]) else 
                                          'No significant difference in masculinity ratings between face sides.'
                    }
                }
                
            # Run femininity test if variables exist
            if has_fem:
                fem_result = run_paired_ttest(r_data, robjects.StrVector(['femininity']))
                results['femininity'] = {
                    'test': 'Paired t-test (Femininity)',
                    'result': {
                        't': fem_result.rx2('t_value')[0],
                        'p': fem_result.rx2('p_value')[0],
                        'df': int(fem_result.rx2('df')[0]),
                        'mean_diff': fem_result.rx2('mean_diff')[0],
                        'effect_size': fem_result.rx2('effect_size')[0],
                        'significant': bool(fem_result.rx2('significant')[0]),
                        'interpretation': 'Significant difference in femininity ratings between face sides.' 
                                          if bool(fem_result.rx2('significant')[0]) else 
                                          'No significant difference in femininity ratings between face sides.'
                    }
                }
                
            return results
            
        except Exception as e:
            return {
                'error': str(e),
                'message': 'Error running paired t-test',
                'status': 'error'
            }
            
    def _run_independent_ttest(self, r_data, variables):
        """
        Run independent samples t-test to determine if there's a difference in trust ratings 
        between male and female participants
        
        Expected variables: ['gender', 'trust']
        """
        try:
            # Check if required variables exist in the dataframe
            if not all(var in r_data.names for var in ['gender', 'trust']):
                return {
                    'error': 'Missing required variables',
                    'message': 'Independent t-test requires gender and trust variables',
                    'status': 'error'
                }
                
            # Define R function for independent t-test
            robjects.r('''
            run_gender_ttest <- function(df) {
              df$gender <- as.factor(df$gender)
              test <- t.test(trust ~ gender, data = df)
              
              # Calculate effect size (Cohen's d)
              gender_levels <- levels(df$gender)
              group1 <- df$trust[df$gender == gender_levels[1]]
              group2 <- df$trust[df$gender == gender_levels[2]]
              
              n1 <- length(group1)
              n2 <- length(group2)
              mean1 <- mean(group1, na.rm = TRUE)
              mean2 <- mean(group2, na.rm = TRUE)
              var1 <- var(group1, na.rm = TRUE)
              var2 <- var(group2, na.rm = TRUE)
              
              # Pooled standard deviation
              sd_pooled <- sqrt(((n1 - 1) * var1 + (n2 - 1) * var2) / (n1 + n2 - 2))
              d <- abs(mean1 - mean2) / sd_pooled
              
              # Create result list
              list(
                t_value = test$statistic,
                p_value = test$p.value,
                df = test$parameter,
                mean_diff = abs(mean1 - mean2),
                effect_size = d,
                significant = test$p.value < 0.05,
                group1_name = gender_levels[1],
                group2_name = gender_levels[2],
                group1_mean = mean1,
                group2_mean = mean2
              )
            }
            ''')
            
            # Run the analysis
            run_gender_ttest = robjects.r['run_gender_ttest']
            result = run_gender_ttest(r_data)
            
            # Convert R result to Python dict
            py_result = {
                'test': 'Independent Samples t-test (Gender)',
                'result': {
                    't': result.rx2('t_value')[0],
                    'p': result.rx2('p_value')[0],
                    'df': result.rx2('df')[0],
                    'mean_diff': result.rx2('mean_diff')[0],
                    'effect_size': result.rx2('effect_size')[0],
                    'significant': bool(result.rx2('significant')[0]),
                    'group1': {
                        'name': result.rx2('group1_name')[0],
                        'mean': result.rx2('group1_mean')[0]
                    },
                    'group2': {
                        'name': result.rx2('group2_name')[0],
                        'mean': result.rx2('group2_mean')[0]
                    },
                    'interpretation': 'Significant difference in trust ratings between genders.' 
                                      if bool(result.rx2('significant')[0]) else 
                                      'No significant difference in trust ratings between genders.'
                }
            }
            
            return py_result
            
        except Exception as e:
            return {
                'error': str(e),
                'message': 'Error running independent t-test',
                'status': 'error'
            }
            
    def _run_correlation(self, r_data, variables):
        """
        Run Pearson correlation to check if there's a linear relationship between 
        perceived masculinity and trust ratings
        
        Expected variables: ['masculinity', 'trust']
        """
        try:
            # Check if required variables exist in the dataframe
            if not all(var in r_data.names for var in ['masculinity', 'trust']):
                return {
                    'error': 'Missing required variables',
                    'message': 'Correlation test requires masculinity and trust variables',
                    'status': 'error'
                }
                
            # Define R function for correlation
            robjects.r('''
            run_correlation <- function(df) {
              test <- cor.test(df$masculinity, df$trust, method = "pearson")
              
              # Create result list
              list(
                correlation = test$estimate,
                p_value = test$p.value,
                df = test$parameter,
                significant = test$p.value < 0.05
              )
            }
            ''')
            
            # Run the analysis
            run_correlation = robjects.r['run_correlation']
            result = run_correlation(r_data)
            
            # Convert R result to Python dict
            py_result = {
                'test': 'Pearson Correlation (Masculinity vs Trust)',
                'result': {
                    'r': result.rx2('correlation')[0],
                    'p': result.rx2('p_value')[0],
                    'df': int(result.rx2('df')[0]),
                    'significant': bool(result.rx2('significant')[0]),
                    'interpretation': f"{'Significant' if bool(result.rx2('significant')[0]) else 'No significant'} correlation between masculinity and trust ratings (r = {result.rx2('correlation')[0]:.2f})."
                }
            }
            
            return py_result
            
        except Exception as e:
            return {
                'error': str(e),
                'message': 'Error running correlation test',
                'status': 'error'
            }
            
    def _run_one_way_anova(self, r_data, variables):
        """
        Run one-way ANOVA to assess if trust ratings differ across age groups
        
        Expected variables: ['age_group', 'trust']
        """
        try:
            # Check if required variables exist in the dataframe
            if not all(var in r_data.names for var in ['age_group', 'trust']):
                return {
                    'error': 'Missing required variables',
                    'message': 'One-way ANOVA requires age_group and trust variables',
                    'status': 'error'
                }
                
            # Define R function for one-way ANOVA
            robjects.r('''
            run_agegroup_anova <- function(df) {
              df$age_group <- as.factor(df$age_group)
              model <- aov(trust ~ age_group, data = df)
              result <- summary(model)
              
              # Extract F-value, p-value, and degrees of freedom
              f_value <- result[[1]]$`F value`[1]
              p_value <- result[[1]]$`Pr(>F)`[1]
              df1 <- result[[1]]$Df[1]
              df2 <- result[[1]]$Df[2]
              
              # Calculate effect size (eta-squared)
              ss_effect <- result[[1]]$`Sum Sq`[1]
              ss_total <- sum(result[[1]]$`Sum Sq`)
              effect_size <- ss_effect / ss_total
              
              # Create result list
              list(
                f_value = f_value,
                p_value = p_value,
                df1 = df1,
                df2 = df2,
                effect_size = effect_size,
                significant = p_value < 0.05
              )
            }
            ''')
            
            # Run the analysis
            run_agegroup_anova = robjects.r['run_agegroup_anova']
            result = run_agegroup_anova(r_data)
            
            # Convert R result to Python dict
            py_result = {
                'test': 'One-Way ANOVA (Age Groups)',
                'result': {
                    'F': result.rx2('f_value')[0],
                    'p': result.rx2('p_value')[0],
                    'df1': int(result.rx2('df1')[0]),
                    'df2': int(result.rx2('df2')[0]),
                    'effect_size': result.rx2('effect_size')[0],
                    'significant': bool(result.rx2('significant')[0]),
                    'interpretation': 'Significant difference in trust ratings between age groups.' 
                                      if bool(result.rx2('significant')[0]) else 
                                      'No significant difference in trust ratings between age groups.'
                }
            }
            
            return py_result
            
        except Exception as e:
            return {
                'error': str(e),
                'message': 'Error running one-way ANOVA',
                'status': 'error'
            }
            
    def _run_descriptive_stats(self, r_data, variables):
        """
        Run descriptive statistics on the data
        """
        try:
            # Define R function for descriptive statistics
            robjects.r('''
            run_descriptive_stats <- function(df) {
              # Get numeric columns
              numeric_cols <- sapply(df, is.numeric)
              numeric_df <- df[, numeric_cols, drop = FALSE]
              
              # Calculate descriptive statistics for each numeric column
              result <- list()
              for (col in names(numeric_df)) {
                col_data <- numeric_df[[col]]
                col_stats <- list(
                  mean = mean(col_data, na.rm = TRUE),
                  median = median(col_data, na.rm = TRUE),
                  sd = sd(col_data, na.rm = TRUE),
                  min = min(col_data, na.rm = TRUE),
                  max = max(col_data, na.rm = TRUE),
                  q1 = quantile(col_data, 0.25, na.rm = TRUE),
                  q3 = quantile(col_data, 0.75, na.rm = TRUE)
                )
                result[[col]] <- col_stats
              }
              
              return(result)
            }
            ''')
            
            # Run the analysis
            run_descriptive_stats = robjects.r['run_descriptive_stats']
            r_result = run_descriptive_stats(r_data)
            
            # Convert R result to Python dict
            py_result = {'test': 'Descriptive Statistics', 'result': {}}
            
            # Extract column names from R result
            col_names = list(r_result.names)
            
            # For each column, extract the statistics
            for col in col_names:
                col_stats = r_result.rx2(col)
                py_result['result'][col] = {
                    'mean': col_stats.rx2('mean')[0],
                    'median': col_stats.rx2('median')[0],
                    'sd': col_stats.rx2('sd')[0],
                    'min': col_stats.rx2('min')[0],
                    'max': col_stats.rx2('max')[0],
                    'q1': col_stats.rx2('q1')[0],
                    'q3': col_stats.rx2('q3')[0]
                }
                
            return py_result
            
        except Exception as e:
            return {
                'error': str(e),
                'message': 'Error running descriptive statistics',
                'status': 'error'
            }
        
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
        """
        Generate mock results based on analysis type
        
        Parameters:
        - analysis_type: Type of analysis (e.g., 'descriptive', 'paired_ttest', etc.)
        - data: Data to analyze (dict with 'columns' and 'rows')
        - variables: Variables to include in the analysis (dict with 'variable' and optional 'secondary_variable')
        
        Returns:
        - Dictionary containing mock analysis results
        """
        print(f"Generating mock results for {analysis_type} analysis with variables: {variables}")
        
        # Validate inputs
        if not variables or 'variable' not in variables:
            return {
                'error': 'Missing required variable',
                'message': 'Primary variable is required',
                'status': 'error'
            }
            
        # Check if variable exists in data
        if 'columns' in data and variables['variable'] not in data['columns']:
            return {
                'error': 'Variable not found',
                'message': f"Variable '{variables['variable']}' not found in data",
                'status': 'error'
            }
            
        # For analyses requiring secondary variable
        if analysis_type in ['paired_ttest', 'independent_ttest', 'correlation', 'one_way_anova'] and (
            'secondary_variable' not in variables or not variables['secondary_variable']):
            return {
                'error': 'Missing secondary variable',
                'message': f"{analysis_type} requires a secondary variable",
                'status': 'error'
            }
            
        # Generate mock results based on analysis type
        result = {
            'analysis_type': analysis_type,
            'variables': variables,
            'status': 'success'
        }
        
        if analysis_type == 'descriptive':
            result['result'] = {
                'mean': 4.2,
                'median': 4.0,
                'sd': 1.2,
                'min': 1.0,
                'max': 7.0,
                'n': len(data['rows']) if 'rows' in data else 30
            }
            
        elif analysis_type == 'paired_ttest':
            result['result'] = {
                't': 3.45,
                'df': 29,
                'p_value': 0.0018,
                'mean_diff': 0.75,
                'ci_lower': 0.32,
                'ci_upper': 1.18
            }
            
        elif analysis_type == 'independent_ttest':
            result['result'] = {
                't': 2.12,
                'df': 28,
                'p_value': 0.043,
                'mean_diff': 0.85,
                'ci_lower': 0.03,
                'ci_upper': 1.67
            }
            
        elif analysis_type == 'correlation':
            result['result'] = {
                'r': 0.65,
                'p_value': 0.0001,
                'n': 30,
                'ci_lower': 0.37,
                'ci_upper': 0.82
            }
            
        elif analysis_type == 'one_way_anova':
            result['result'] = {
                'F': 4.78,
                'df_between': 3,
                'df_within': 26,
                'p_value': 0.009,
                'eta_squared': 0.36
            }
            
        elif analysis_type == 'repeated_measures_anova':
            result['result'] = {
                'F': 5.23,
                'df_factor': 1,
                'df_error': 29,
                'p_value': 0.003,
                'eta_squared': 0.28
            }
            
        else:
            result = {
                'error': 'Invalid analysis type',
                'message': f"Analysis type '{analysis_type}' not supported",
                'status': 'error'
            }
            
        return result
        
    def available_analyses(self):
        """Return list of available analyses"""
        return [
            {
                'id': 'descriptive',
                'name': 'Descriptive Statistics',
                'description': 'Summary statistics (mean, median, SD, etc.)',
                'min_variables': 1,
                'max_variables': 1,
                'requires_secondary': False
            },
            {
                'id': 'paired_ttest',
                'name': 'Paired T-Test',
                'description': 'Compare means between paired measurements',
                'min_variables': 2,
                'max_variables': 2,
                'requires_secondary': True
            },
            {
                'id': 'independent_ttest',
                'name': 'Independent T-Test',
                'description': 'Compare means between independent groups',
                'min_variables': 2,
                'max_variables': 2,
                'requires_secondary': True
            },
            {
                'id': 'one_way_anova',
                'name': 'One-Way ANOVA',
                'description': 'Analysis of variance between groups',
                'min_variables': 2,
                'max_variables': 2,
                'requires_secondary': True
            },
            {
                'id': 'repeated_measures_anova',
                'name': 'Repeated Measures ANOVA',
                'description': 'Analysis of variance for repeated measurements',
                'min_variables': 2,
                'max_variables': 3,
                'requires_secondary': True
            },
            {
                'id': 'correlation',
                'name': 'Correlation',
                'description': 'Measure relationship between variables',
                'min_variables': 2,
                'max_variables': 2,
                'requires_secondary': True
            }
        ]
