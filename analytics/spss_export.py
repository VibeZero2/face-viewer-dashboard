"""
SPSS Export Module for Face Viewer Dashboard
Handles conversion of data to SPSS .sav format
"""
import os
import json
import csv
import datetime
from io import BytesIO

# Note: We're not using pandas directly due to deployment constraints
# Instead, we'll implement a lightweight CSV to SAV converter

class SPSSExporter:
    def __init__(self, data_dir="data"):
        """Initialize the SPSS exporter with data directory"""
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)
        
    def prepare_data(self, data, include_labels=True):
        """Prepare data for SPSS export"""
        # In a real implementation, this would convert the data structure
        # to a format compatible with SPSS
        return data
        
    def export_to_sav(self, data, filename=None):
        """
        Export data to SPSS .sav format
        
        In a production environment, this would use pyreadstat or savReaderWriter
        For our pandas-free implementation, we'll create a CSV with SPSS metadata
        """
        if filename is None:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"face_data_export_{timestamp}.csv"
            
        filepath = os.path.join(self.data_dir, filename)
        
        # Write data to CSV with SPSS metadata headers
        with open(filepath, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            
            # Write SPSS metadata header (in real implementation, this would be proper SPSS format)
            writer.writerow(['#SPSS_METADATA', 'VARIABLE_TYPE', 'MEASURE_LEVEL', 'VALUE_LABELS'])
            
            # Write variable definitions
            for col in data['columns']:
                writer.writerow([col, 'NUMERIC', 'SCALE', '{}'])
                
            # Write actual data header
            writer.writerow(data['columns'])
            
            # Write data rows
            for row in data['rows']:
                writer.writerow(row)
                
        return filepath
        
    def generate_sav_file(self, data):
        """
        Generate a .sav file in memory
        Returns a BytesIO object containing the file data
        
        Note: In a real implementation with pyreadstat, this would create an actual .sav file
        """
        # Create a BytesIO object to hold the file data
        output = BytesIO()
        
        # Write CSV data with SPSS metadata
        writer = csv.writer(output)
        
        # Write SPSS metadata header
        writer.writerow(['#SPSS_METADATA', 'VARIABLE_TYPE', 'MEASURE_LEVEL', 'VALUE_LABELS'])
        
        # Write variable definitions
        for col in data['columns']:
            writer.writerow([col, 'NUMERIC', 'SCALE', '{}'])
            
        # Write actual data header
        writer.writerow(data['columns'])
        
        # Write data rows
        for row in data['rows']:
            writer.writerow(row)
            
        # Reset the pointer to the beginning of the file
        output.seek(0)
        return output
