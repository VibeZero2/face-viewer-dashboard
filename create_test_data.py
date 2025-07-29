"""
Test data generator for Face Viewer Dashboard
Creates sample participant CSV files in data/responses/ directory
"""

import os
import csv
import random
from datetime import datetime, timedelta

# Ensure directories exist
RESPONSES_DIR = os.path.join(os.getcwd(), 'data', 'responses')
os.makedirs(RESPONSES_DIR, exist_ok=True)

def create_test_participant_data(num_participants=5, responses_per_participant=10):
    """Create sample participant data files for testing"""
    
    print(f"Creating {num_participants} test participant files with {responses_per_participant} responses each")
    
    # Face versions
    face_versions = ["Full Face", "Left Half", "Right Half"]
    
    # Create data for each participant
    for p_idx in range(1, num_participants + 1):
        participant_id = f"TEST{p_idx:03d}"
        filename = f"test_participant_{p_idx}.csv"
        filepath = os.path.join(RESPONSES_DIR, filename)
        
        # Generate random start time for this participant
        start_time = datetime.now() - timedelta(days=random.randint(1, 30))
        
        # Create the CSV file
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            # Define CSV columns
            fieldnames = [
                'Participant ID', 'Face', 'Version', 'Trust', 'Emotion',
                'Masculinity', 'Femininity', 'Timestamp'
            ]
            
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            
            # Write responses for this participant
            for r_idx in range(1, responses_per_participant + 1):
                # Randomize face version
                version = random.choice(face_versions)
                
                # Generate response time (sequential from start time)
                response_time = start_time + timedelta(minutes=r_idx * 2)
                
                # Generate random ratings
                trust_rating = round(random.uniform(1.0, 7.0), 1)
                emotion_rating = round(random.uniform(1.0, 7.0), 1)
                masculinity = round(random.uniform(1.0, 7.0), 1)
                femininity = round(random.uniform(1.0, 7.0), 1)
                
                # Write the row
                writer.writerow({
                    'Participant ID': participant_id,
                    'Face': f"face_{r_idx:02d}.jpg",
                    'Version': version,
                    'Trust': trust_rating,
                    'Emotion': emotion_rating,
                    'Masculinity': masculinity,
                    'Femininity': femininity,
                    'Timestamp': response_time.strftime('%Y-%m-%d %H:%M:%S')
                })
        
        print(f"Created {filepath} with {responses_per_participant} responses")
    
    print(f"Test data generation complete. {num_participants} files created in {RESPONSES_DIR}")

if __name__ == "__main__":
    # Generate test data
    create_test_participant_data(num_participants=5, responses_per_participant=10)
    print("Done!")
