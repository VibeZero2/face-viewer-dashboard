import os
import csv
import logging

# Configure logging
logger = logging.getLogger(__name__)

# Define a consistent path for responses directory
RESPONSES_DIR = os.path.join(os.getcwd(), 'data', 'responses')

def safe_float(value, default=0.0):
    """
    Safely convert a value to float, returning a default if conversion fails.
    
    Args:
        value: Value to convert to float
        default: Default value to return if conversion fails
        
    Returns:
        float value or default if conversion fails
    """
    try:
        if value is None or value == '':
            return default
        return float(value)
    except (TypeError, ValueError):
        return default

def load_all_participant_data(responses_dir=None):
    """
    Loads all participant CSVs from the responses directory.
    Returns a list of dicts, each representing a row from a CSV file.
    Skips files that can't be parsed and adds a 'participant_file' field to each row.
    
    Args:
        responses_dir: Optional directory path. If None, uses the default RESPONSES_DIR.
    """
    # Use the default directory if none provided
    if responses_dir is None:
        responses_dir = RESPONSES_DIR
        
    combined = []
    
    # Create directory if it doesn't exist
    try:
        os.makedirs(responses_dir, exist_ok=True)
        logger.info(f"Using responses directory: {responses_dir}")
    except Exception as e:
        logger.error(f"Failed to create responses directory {responses_dir}: {e}")
        return combined
    
    if not os.path.exists(responses_dir):
        logger.warning(f"Responses directory does not exist after creation attempt: {responses_dir}")
        return combined
        
    # Count files for logging
    try:
        csv_files = [f for f in os.listdir(responses_dir) if f.endswith(".csv")]
        logger.info(f"Found {len(csv_files)} files in {responses_dir}")
    except Exception as e:
        logger.error(f"Error listing directory {responses_dir}: {e}")
        return combined
    
    # Process each CSV file
    for filename in csv_files:
        filepath = os.path.join(responses_dir, filename)
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                
                # Validate CSV headers
                headers = reader.fieldnames
                if not headers:
                    logger.warning(f"File {filename} has no headers")
                    continue
                    
                # Check for required headers
                if "Participant ID" not in headers and "ParticipantID" not in headers:
                    logger.warning(f"File {filename} missing required 'Participant ID' column")
                    # Continue processing anyway, but log the warning
                
                file_rows = 0
                for row in reader:
                    if any(row.values()):  # skip empty rows
                        # Add defensive defaults for missing columns
                        row["participant_file"] = filename
                        
                        # Handle different column naming conventions and missing values
                        # Participant ID handling
                        if "Participant ID" not in row and "ParticipantID" in row:
                            row["Participant ID"] = row["ParticipantID"]
                        row.setdefault("Participant ID", f"Unknown-{filename}-{file_rows}")
                        
                        # Required columns for charts and analysis
                        row.setdefault("Trust", None)
                        row.setdefault("Masculinity", None)
                        row.setdefault("Femininity", None)
                        row.setdefault("Symmetry", None)
                        row.setdefault("FaceVersion", "Unknown")
                        row.setdefault("FaceNumber", "Unknown")
                        row.setdefault("FaceID", f"Face-{file_rows}")
                        
                        combined.append(row)
                        file_rows += 1
                logger.info(f"Loaded {file_rows} rows from {filename}")
        except csv.Error as e:
            logger.error(f"CSV parsing error in {filename}: {e}")
            continue
        except IOError as e:
            logger.error(f"I/O error reading {filename}: {e}")
            continue
        except Exception as e:
            logger.error(f"Unexpected error reading {filename}: {e}")
            continue
    
    logger.info(f"Total rows loaded from all CSVs: {len(combined)}")
    return combined
