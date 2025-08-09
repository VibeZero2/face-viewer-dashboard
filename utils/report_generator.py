"""
Report generation utilities for Face Viewer Dashboard
"""
import os
import logging
import tempfile
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional, Union
import jinja2
import pdfkit
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import numpy as np
import base64
import io

# Import utilities
from utils.csv_loader import load_csv_files, filter_data
from utils.analysis import run_analysis

# Set up logging
log = logging.getLogger(__name__)

# Set up Jinja2 environment
template_dir = Path(__file__).parent.parent / 'templates'
jinja_env = jinja2.Environment(
    loader=jinja2.FileSystemLoader(template_dir),
    autoescape=jinja2.select_autoescape(['html', 'xml'])
)

def generate_plot(data: List[Dict[str, Any]], variable: str, title: str = None) -> str:
    """
    Generate a base64-encoded plot image
    
    Args:
        data: List of data dictionaries
        variable: Variable to plot
        title: Plot title
        
    Returns:
        Base64-encoded PNG image
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
        return None
    
    # Create figure
    plt.figure(figsize=(8, 6))
    
    # Create histogram
    plt.hist(values, bins=10, alpha=0.7, color='skyblue', edgecolor='black')
    
    # Add title and labels
    if title:
        plt.title(title)
    else:
        plt.title(f'Distribution of {variable}')
    plt.xlabel(variable)
    plt.ylabel('Frequency')
    
    # Add grid
    plt.grid(axis='y', alpha=0.75)
    
    # Save to buffer
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    plt.close()
    
    # Convert to base64
    buffer.seek(0)
    image_png = buffer.getvalue()
    buffer.close()
    
    encoded = base64.b64encode(image_png).decode('utf-8')
    return f"data:image/png;base64,{encoded}"

def generate_html_report(
    test_type: str, 
    variable: str, 
    filters: Dict[str, Any] = None, 
    secondary_variable: str = None
) -> str:
    """
    Generate an HTML report for the specified analysis
    
    Args:
        test_type: Type of test ('descriptives', 'ttest', 'wilcoxon', 'correlation')
        variable: Variable to analyze
        filters: Filters to apply to the data
        secondary_variable: Secondary variable (for correlation)
        
    Returns:
        HTML report content
    """
    try:
        # Load and filter data
        data = load_csv_files()
        if filters:
            data = filter_data(data, filters)
        
        if not data:
            return "<h1>Error</h1><p>No data found matching the specified filters.</p>"
        
        # Run the analysis
        analysis_result = run_analysis(test_type, variable, filters, secondary_variable)
        
        # Generate plots
        variable_plot = generate_plot(data, variable, f'Distribution of {variable}')
        secondary_plot = None
        if secondary_variable:
            secondary_plot = generate_plot(data, secondary_variable, f'Distribution of {secondary_variable}')
        
        # Load the template
        template = jinja_env.get_template('report.html')
        
        # Render the template
        html_content = template.render(
            title=f"Face Analysis Report - {test_type.capitalize()}",
            timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            test_type=test_type,
            variable=variable,
            secondary_variable=secondary_variable,
            filters=filters,
            result=analysis_result,
            variable_plot=variable_plot,
            secondary_plot=secondary_plot,
            data_count=len(data)
        )
        
        return html_content
        
    except Exception as e:
        log.error(f"Error in generate_html_report: {str(e)}", exc_info=True)
        return f"<h1>Error</h1><p>An error occurred while generating the report: {str(e)}</p>"

def generate_pdf_report(
    test_type: str, 
    variable: str, 
    filters: Dict[str, Any] = None, 
    secondary_variable: str = None
) -> bytes:
    """
    Generate a PDF report for the specified analysis
    
    Args:
        test_type: Type of test ('descriptives', 'ttest', 'wilcoxon', 'correlation')
        variable: Variable to analyze
        filters: Filters to apply to the data
        secondary_variable: Secondary variable (for correlation)
        
    Returns:
        PDF report content as bytes
    """
    try:
        # Generate HTML report
        html_content = generate_html_report(test_type, variable, filters, secondary_variable)
        
        # Convert HTML to PDF
        pdf_options = {
            'page-size': 'A4',
            'margin-top': '0.75in',
            'margin-right': '0.75in',
            'margin-bottom': '0.75in',
            'margin-left': '0.75in',
            'encoding': 'UTF-8',
            'no-outline': None
        }
        
        # Create a temporary file for the PDF
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_pdf:
            temp_pdf_path = temp_pdf.name
        
        # Convert HTML to PDF
        pdfkit.from_string(html_content, temp_pdf_path, options=pdf_options)
        
        # Read the PDF file
        with open(temp_pdf_path, 'rb') as f:
            pdf_content = f.read()
        
        # Delete the temporary file
        os.unlink(temp_pdf_path)
        
        return pdf_content
        
    except Exception as e:
        log.error(f"Error in generate_pdf_report: {str(e)}", exc_info=True)
        return None
