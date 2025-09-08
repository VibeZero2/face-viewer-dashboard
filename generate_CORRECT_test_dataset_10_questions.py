#!/usr/bin/env python3
"""
Generate CORRECT test dataset for facial trust study with EXACT specifications:
- 65 participants  
- 35 faces (face_id 1-35)
- 10 questions per face (3 trust + 7 personality questions)
- Total: 22,750 responses (65 × 35 × 10)
"""

import pandas as pd
import random
import os
from datetime import datetime, timedelta

def generate_correct_test_dataset_10_questions():
    """Generate test dataset with EXACT study specifications - 10 questions per face."""
    
    # Study parameters - CORRECTED
    num_participants = 65
    num_faces = 35
    questions_per_face = 10  # This is the key fix!
    
    print("🎯 GENERATING CORRECT TEST DATASET - 10 QUESTIONS PER FACE")
    print("=" * 60)
    print(f"Participants: {num_participants}")
    print(f"Faces: {num_faces} (face_id 1-35)")
    print(f"Questions per face: {questions_per_face}")
    print(f"Expected responses per participant: {num_faces * questions_per_face}")
    print(f"Expected total responses: {num_participants * num_faces * questions_per_face}")
    print()
    
    # Question types for each face (10 total)
    question_types = [
        # Trust questions (3)
        "trust_rating_left", "trust_rating_right", "trust_rating_full",
        # Personality questions (7) 
        "pers_q1", "pers_q2", "pers_q3", "pers_q4", "pers_q5", "pers_q6", "pers_q7"
    ]
    
    # Generate all data
    all_data = []
    
    for participant_num in range(1, num_participants + 1):
        participant_id = f"p{participant_num:03d}"  # p001, p002, ..., p065
        
        # Generate session timestamp
        session_time = datetime.now() - timedelta(days=random.randint(1, 14))
        
        for face_id in range(1, num_faces + 1):
            for question_idx, question_type in enumerate(question_types):
                # Generate timestamp for this specific response
                response_time = session_time + timedelta(
                    minutes=random.randint(-30, 30),
                    seconds=random.randint(0, 59)
                )
                
                # Determine face view and question based on question_type
                if "left" in question_type:
                    face_view = "left"
                    base_question = question_type.replace("_left", "")
                elif "right" in question_type:
                    face_view = "right"  
                    base_question = question_type.replace("_right", "")
                elif "full" in question_type:
                    face_view = "full"
                    base_question = question_type.replace("_full", "")
                else:
                    face_view = random.choice(["left", "right", "full"])
                    base_question = question_type
                
                # Generate response values
                trust_rating = random.randint(1, 7)
                masc_choice = random.choice(["left", "right", "neither"])
                fem_choice = random.choice(["left", "right", "neither"])
                emotion_rating = random.randint(1, 10)
                
                # Generate personality question responses
                trust_q2 = random.randint(1, 7) if random.random() > 0.2 else ""
                trust_q3 = random.randint(1, 7) if random.random() > 0.2 else ""
                pers_q1 = random.randint(1, 7) if random.random() > 0.2 else ""
                pers_q2 = random.randint(1, 7) if random.random() > 0.2 else ""
                pers_q3 = random.randint(1, 7) if random.random() > 0.2 else ""
                pers_q4 = random.randint(1, 7) if random.random() > 0.2 else ""
                pers_q5 = random.randint(1, 7) if random.random() > 0.2 else ""
                
                # Create response row in dashboard format
                response = {
                    "pid": participant_id.replace('p', ''),  # Remove 'p' prefix for dashboard
                    "timestamp": response_time.strftime("%Y-%m-%dT%H:%M:%S.%f"),
                    "face_id": f"{face_id} (100)",  # Dashboard format
                    "version": face_view,
                    "order_presented": question_idx,
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
                    "prolific_pid": f"TEST_{participant_id}"
                }
                
                all_data.append(response)
    
    # Create DataFrame
    df = pd.DataFrame(all_data)
    
    # Verify structure
    print("📊 VERIFICATION:")
    print(f"Total rows: {len(df):,}")
    print(f"Unique participants: {df['pid'].nunique()}")
    print(f"Unique face_ids: {df['face_id'].nunique()}")
    print(f"Face views: {sorted(df['version'].unique())}")
    print(f"Responses per participant: {len(df) // num_participants}")
    print(f"Expected responses per participant: {num_faces * questions_per_face}")
    
    # Verify we have correct number of responses
    expected_total = num_participants * num_faces * questions_per_face
    if len(df) == expected_total:
        print(f"✅ CORRECT: {len(df):,} responses (expected {expected_total:,})")
    else:
        print(f"❌ ERROR: {len(df):,} responses (expected {expected_total:,})")
    
    print()
    
    # Save individual participant files for dashboard compatibility
    print("📁 GENERATING INDIVIDUAL PARTICIPANT FILES:")
    for participant_id in df['pid'].unique():
        participant_data = df[df['pid'] == participant_id].copy()
        
        # Create filename
        timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"data/responses/test_p{participant_id.zfill(3)}_{timestamp_str}.csv"
        
        # Save file
        participant_data.to_csv(filename, index=False)
        print(f"  ✅ Participant {participant_id}: {len(participant_data)} responses → {filename}")
    
    print(f"\n🎉 SUCCESS!")
    print(f"📊 Generated {num_participants} participants with {len(df):,} total responses")
    print(f"📁 Individual files saved in: data/responses/")
    print(f"🔄 Dashboard should now show:")
    print(f"   - {num_participants} Total Participants")
    print(f"   - {len(df):,} Total Responses") 
    print(f"   - {len(df) // num_participants} Responses per participant")
    
    return df

if __name__ == "__main__":
    df = generate_correct_test_dataset_10_questions()
