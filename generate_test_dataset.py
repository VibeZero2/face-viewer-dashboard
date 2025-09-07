#!/usr/bin/env python3
"""
Generate Full Test Dataset for Facial Trust Study Dashboard Validation
Simulates 60 participants completing the full facial trust rating study.
"""

import csv
import random
from datetime import datetime, timedelta
import os

def generate_test_dataset():
    """Generate 65 participants with complete facial trust study data."""
    
    # Ensure data directory exists
    os.makedirs("data/responses", exist_ok=True)
    
    # Study parameters - CORRECTED FOR 10 QUESTIONS PER FACE
    num_participants = 65
    participant_start_id = 200
    num_faces = 35
    questions_per_face = 10
    rating_scale = (1, 7)  # 1-7 scale
    
    # Generate random timestamps within the last 14 days
    end_time = datetime.now()
    start_time = end_time - timedelta(days=14)
    
    print(f"Generating test dataset for {num_participants} participants...")
    print(f"Each participant will rate {num_faces} faces × 3 versions = {num_faces * 3} responses")
    print(f"Total expected responses: {num_participants * num_faces * 3}")
    
    for participant_num in range(num_participants):
        participant_id = participant_start_id + participant_num
        
        # Generate a random timestamp for this participant's session
        session_time = start_time + timedelta(
            seconds=random.randint(0, int((end_time - start_time).total_seconds()))
        )
        
        # Create filename with TEST prefix to clearly identify as test data
        timestamp_str = session_time.strftime("%Y%m%d_%H%M%S")
        filename = f"data/responses/test_participant_{participant_id}_{timestamp_str}.csv"
        
        # Generate data for this participant in WIDE FORMAT (matching real study data)
        rows = []
        
        for face_num in range(1, num_faces + 1):
            # Use consistent face_id format - same 35 faces for all participants
            face_id = f"{face_num}"
            
            # Generate 3 versions per face (left, right, full) like real study data
            for view_idx, view in enumerate(["left", "right", "full"]):
                # Generate timestamp for this specific rating
                rating_time = session_time + timedelta(
                    minutes=random.randint(-30, 30),
                    seconds=random.randint(0, 59)
                )
                
                # Generate random ratings for each question type
                trust_rating = random.randint(*rating_scale)
                masc_choice = random.choice(["left", "right", "neither"])
                fem_choice = random.choice(["left", "right", "neither"])
                emotion_rating = random.randint(*rating_scale)
                
                # Create row with all questions, but some may be empty like real data
                row = {
                    "pid": participant_id,
                    "timestamp": rating_time.strftime("%Y-%m-%dT%H:%M:%S.%f"),
                    "face_id": face_id,
                    "version": view,
                    "order_presented": view_idx,
                    "trust_rating": trust_rating,
                    "masc_choice": masc_choice,
                    "fem_choice": fem_choice,
                    "emotion_rating": emotion_rating,
                    "trust_q2": random.randint(*rating_scale) if random.random() > 0.3 else "",
                    "trust_q3": random.randint(*rating_scale) if random.random() > 0.3 else "",
                    "pers_q1": random.randint(*rating_scale) if random.random() > 0.3 else "",
                    "pers_q2": random.randint(*rating_scale) if random.random() > 0.3 else "",
                    "pers_q3": random.randint(*rating_scale) if random.random() > 0.3 else "",
                    "pers_q4": random.randint(*rating_scale) if random.random() > 0.3 else "",
                    "pers_q5": random.randint(*rating_scale) if random.random() > 0.3 else "",
                    "prolific_pid": f"TEST_{participant_id}"
                }
                rows.append(row)
        
        # Write CSV file in WIDE FORMAT
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ["pid", "timestamp", "face_id", "version", "order_presented", "trust_rating", 
                         "masc_choice", "fem_choice", "emotion_rating", "trust_q2", "trust_q3", 
                         "pers_q1", "pers_q2", "pers_q3", "pers_q4", "pers_q5", "prolific_pid"]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
        
        print(f"Generated participant {participant_id}: {len(rows)} ratings → {filename}")
    
    print(f"\n✅ Test dataset generation complete!")
    print(f"📊 Generated {num_participants} participant files")
    print(f"📈 Total responses: {num_participants * num_faces * 3}")
    print(f"📁 Files saved in: data/responses/")
    print(f"\n🔄 The dashboard should automatically detect these files and update...")
    print(f"🎯 Expected dashboard metrics:")
    print(f"   - Participants: {num_participants}")
    print(f"   - Responses per participant: {num_faces * 3}")
    print(f"   - Total rows loaded: {num_participants * num_faces * 3}")

if __name__ == "__main__":
    generate_test_dataset()
