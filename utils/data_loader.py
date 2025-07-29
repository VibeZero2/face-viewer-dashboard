import os
import csv
import logging

# Configure logging
logger = logging.getLogger(__name__)

def load_all_participant_data(responses_dir):
    """
    Loads all participant CSVs from the responses directory.
    Returns a list of dicts, each representing a row from a CSV file.
    Skips files that can't be parsed and adds a 'participant_file' field to each row.
    """
    combined = []
    
    # Create directory if it doesn't exist
    os.makedirs(responses_dir, exist_ok=True)
    
    if not os.path.exists(responses_dir):
        logger.warning(f"Responses directory does not exist: {responses_dir}")
        return combined
        
    # Count files for logging
    csv_files = [f for f in os.listdir(responses_dir) if f.endswith(".csv")]
    logger.info(f"Found {len(csv_files)} files in {responses_dir}")
    
    # Process each CSV file
    for filename in csv_files:
        filepath = os.path.join(responses_dir, filename)
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                file_rows = 0
                for row in reader:
                    if any(row.values()):  # skip empty rows
                        row["participant_file"] = filename
                        combined.append(row)
                        file_rows += 1
                logger.info(f"Loaded {file_rows} rows from {filename}")
        except Exception as e:
            logger.error(f"Error reading {filename}: {e}")
            continue
    
    logger.info(f"Total rows loaded from all CSVs: {len(combined)}")
    return combined
