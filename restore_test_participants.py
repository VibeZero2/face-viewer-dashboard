#!/usr/bin/env python3
"""
Restore individual test participant files from the combined dataset
"""
import pandas as pd
import os
from pathlib import Path

def restore_test_participants():
    # Read the combined test data
    df = pd.read_csv('all_test_participant_data.csv')
    
    # Get the study program data directory
    study_data_dir = Path("../facial-trust-study/data/responses")
    study_data_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"Found {df['pid'].nunique()} unique participants in combined data")
    
    # Group by participant ID and source file
    for (pid, source_file), group in df.groupby(['pid', 'source_file']):
        # Create filename based on source_file
        filename = source_file
        if not filename.endswith('.csv'):
            filename += '.csv'
        
        # Save to study program data directory
        output_path = study_data_dir / filename
        group.to_csv(output_path, index=False)
        print(f"Restored {len(group)} rows to {filename}")
    
    print(f"Restored {df['source_file'].nunique()} test participant files to {study_data_dir}")

if __name__ == "__main__":
    restore_test_participants()

