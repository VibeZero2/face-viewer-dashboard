#!/usr/bin/env python3
"""
Generate correct test dataset for facial trust study with exact specifications:
- 65 participants
- 35 faces (face_id 1-35)
- 3 views per face (left, right, full)
- 10 questions per face
- Total: 6,825 responses (65 × 35 × 3)
"""

import pandas as pd
import random
import os
from datetime import datetime, timedelta

def generate_correct_test_dataset():
    """Generate test dataset with exact study specifications."""
    
    # Study parameters
    num_participants = 65
    num_faces = 35
    face_views = ["left", "right", "full"]
    
    print("🎯 GENERATING CORRECT TEST DATASET")
    print("=" * 50)
    print(f"Participants: {num_participants}")
    print(f"Faces: {num_faces} (face_id 1-35)")
    print(f"Views per face: {len(face_views)} ({', '.join(face_views)})")
    print(f"Questions per face: 10")
    print(f"Total responses: {num_participants * num_faces * len(face_views)}")
    print()
    
    # Generate all data
    all_data = []
    
    for participant_num in range(1, num_participants + 1):
        participant_id = f"P{participant_num:03d}"  # P001, P002, ..., P065
        
        # Generate session timestamp
        session_time = datetime.now() - timedelta(days=random.randint(1, 14))
        
        for face_id in range(1, num_faces + 1):
            for view_idx, face_view in enumerate(face_views):
                # Generate timestamp for this specific response
                response_time = session_time + timedelta(
                    minutes=random.randint(-30, 30),
                    seconds=random.randint(0, 59)
                )
                
                # Generate required values (never empty)
                trust_rating = random.randint(1, 7)
                masc_choice = random.choice(["Left", "Right", "Neither"])
                fem_choice = random.choice(["Left", "Right", "Neither"])
                emotion_rating = random.randint(1, 10)
                
                # Generate optional values (30% chance of being empty)
                trust_q2 = random.randint(1, 7) if random.random() > 0.3 else None
                trust_q3 = random.randint(1, 7) if random.random() > 0.3 else None
                pers_q1 = random.randint(1, 7) if random.random() > 0.3 else None
                pers_q2 = random.randint(1, 7) if random.random() > 0.3 else None
                pers_q3 = random.randint(1, 7) if random.random() > 0.3 else None
                pers_q4 = random.randint(1, 7) if random.random() > 0.3 else None
                pers_q5 = random.randint(1, 7) if random.random() > 0.3 else None
                
                # Create response row
                response = {
                    "participant_id": participant_id,
                    "face_id": face_id,
                    "face_view": face_view,
                    "trust_rating": trust_rating,
                    "masc_choice": masc_choice,
                    "fem_choice": fem_choice,
                    "emotion_rating": emotion_rating,
                    "trust_q2": trust_q2,
                    "trust_q3": trust_q3,
                    "pers_q1": pers_q1,
                    "pers_q2": pers_q2,
                    "pers_q3": pers_q3,
                    "pers_q4": pers_q4,
                    "pers_q5": pers_q5,
                    "timestamp": response_time.strftime("%Y-%m-%dT%H:%M:%S.%f")
                }
                
                all_data.append(response)
    
    # Create DataFrame
    df = pd.DataFrame(all_data)
    
    # Verify structure
    print("📊 VERIFICATION:")
    print(f"Total rows: {len(df)}")
    print(f"Unique participants: {df['participant_id'].nunique()}")
    print(f"Unique face_ids: {df['face_id'].nunique()}")
    print(f"Face views: {sorted(df['face_view'].unique())}")
    print(f"Responses per participant: {len(df) // num_participants}")
    print()
    
    # Check for missing values in required columns
    required_cols = ["trust_rating", "masc_choice", "fem_choice", "emotion_rating"]
    for col in required_cols:
        missing = df[col].isna().sum()
        print(f"{col}: {missing} missing values {'✅' if missing == 0 else '❌'}")
    
    # Check optional columns (should have some missing values)
    optional_cols = ["trust_q2", "trust_q3", "pers_q1", "pers_q2", "pers_q3", "pers_q4", "pers_q5"]
    for col in optional_cols:
        missing = df[col].isna().sum()
        print(f"{col}: {missing} missing values ({missing/len(df)*100:.1f}%)")
    
    print()
    
    # Save the dataset
    output_file = "test_full_dataset_with_10_questions.csv"
    df.to_csv(output_file, index=False)
    print(f"💾 SAVED: {output_file}")
    print(f"📁 File size: {os.path.getsize(output_file) / 1024:.1f} KB")
    
    # Also save individual participant files for dashboard compatibility
    os.makedirs("data/responses", exist_ok=True)
    
    print("\n📁 GENERATING INDIVIDUAL PARTICIPANT FILES:")
    for participant_id in df['participant_id'].unique():
        participant_data = df[df['participant_id'] == participant_id].copy()
        
        # Add columns for dashboard compatibility
        participant_data['pid'] = participant_id.replace('P', '')
        participant_data['version'] = participant_data['face_view']
        participant_data['order_presented'] = participant_data.groupby('face_id').cumcount()
        participant_data['prolific_pid'] = f"TEST_{participant_id}"
        participant_data['source_file'] = f"test_{participant_id.lower()}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        # Reorder columns for dashboard compatibility
        dashboard_cols = [
            'pid', 'timestamp', 'face_id', 'version', 'order_presented',
            'trust_rating', 'masc_choice', 'fem_choice', 'emotion_rating',
            'trust_q2', 'trust_q3', 'pers_q1', 'pers_q2', 'pers_q3', 'pers_q4', 'pers_q5',
            'prolific_pid', 'source_file'
        ]
        
        participant_data = participant_data[dashboard_cols]
        
        # Save individual file
        filename = f"data/responses/test_{participant_id.lower()}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        participant_data.to_csv(filename, index=False)
        print(f"  ✅ {participant_id}: {len(participant_data)} responses")
    
    print(f"\n🎉 SUCCESS!")
    print(f"📊 Generated {num_participants} participants with {len(df)} total responses")
    print(f"📁 Main dataset: {output_file}")
    print(f"📁 Individual files: data/responses/")
    print(f"🔄 Dashboard should now show correct data structure!")
    
    return df

if __name__ == "__main__":
    df = generate_correct_test_dataset()
