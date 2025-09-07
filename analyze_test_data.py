#!/usr/bin/env python3
"""
Script to analyze all test participant data and create a combined dataset
for verification that the system is processing it correctly.
"""

import pandas as pd
import glob
import os
from pathlib import Path

def analyze_test_data():
    print("🔍 ANALYZING ALL TEST PARTICIPANT DATA")
    print("=" * 50)
    
    # Get all test participant files
    test_files = glob.glob('data/responses/test_participant_*.csv')
    test_files.sort()
    
    print(f"📁 Found {len(test_files)} test participant files:")
    for i, file in enumerate(test_files, 1):
        filename = os.path.basename(file)
        print(f"  {i:2d}. {filename}")
    
    print(f"\n📊 LOADING AND COMBINING DATA...")
    
    # Load and combine all test data
    all_data = []
    total_rows = 0
    
    for file in test_files:
        try:
            df = pd.read_csv(file)
            df['source_file'] = os.path.basename(file)
            all_data.append(df)
            total_rows += len(df)
            print(f"  ✅ {os.path.basename(file)}: {len(df)} rows")
        except Exception as e:
            print(f"  ❌ ERROR loading {file}: {e}")
    
    if not all_data:
        print("❌ No test data could be loaded!")
        return
    
    # Combine all data
    combined = pd.concat(all_data, ignore_index=True)
    
    print(f"\n📈 COMBINED DATA SUMMARY:")
    print(f"  Total rows: {len(combined):,}")
    print(f"  Total files: {len(all_data)}")
    print(f"  Columns: {list(combined.columns)}")
    
    # Analyze participants
    unique_participants = combined['pid'].nunique()
    print(f"\n👥 PARTICIPANT ANALYSIS:")
    print(f"  Unique participants: {unique_participants}")
    print(f"  Expected participants: 65")
    print(f"  Match: {'✅ YES' if unique_participants == 65 else '❌ NO'}")
    
    # Analyze face IDs
    unique_faces = combined['face_id'].nunique()
    face_ids = sorted(combined['face_id'].unique())
    print(f"\n🖼️  FACE ID ANALYSIS:")
    print(f"  Unique face_ids: {unique_faces}")
    print(f"  Expected face_ids: 35")
    print(f"  Match: {'✅ YES' if unique_faces == 35 else '❌ NO'}")
    print(f"  Face ID range: {face_ids[:5]}...{face_ids[-5:] if len(face_ids) > 10 else face_ids}")
    
    # Analyze versions
    versions = combined['version'].unique()
    print(f"\n🔄 VERSION ANALYSIS:")
    print(f"  Versions: {list(versions)}")
    print(f"  Expected: ['full', 'left', 'right']")
    
    # Analyze responses per participant
    responses_per_participant = combined.groupby('pid').size()
    print(f"\n📝 RESPONSES PER PARTICIPANT:")
    print(f"  Min responses: {responses_per_participant.min()}")
    print(f"  Max responses: {responses_per_participant.max()}")
    print(f"  Mean responses: {responses_per_participant.mean():.1f}")
    print(f"  Expected: 105 (35 faces × 3 versions)")
    
    # Check for expected structure
    expected_responses = 65 * 35 * 3  # 65 participants × 35 faces × 3 versions
    print(f"\n🎯 STRUCTURE VERIFICATION:")
    print(f"  Actual total responses: {len(combined):,}")
    print(f"  Expected total responses: {expected_responses:,}")
    print(f"  Structure match: {'✅ YES' if len(combined) == expected_responses else '❌ NO'}")
    
    # Save combined data
    output_file = 'all_test_participant_data.csv'
    combined.to_csv(output_file, index=False)
    print(f"\n💾 SAVED COMBINED DATA:")
    print(f"  File: {output_file}")
    print(f"  Size: {os.path.getsize(output_file) / 1024:.1f} KB")
    
    # Show sample data
    print(f"\n📋 SAMPLE DATA (first 10 rows):")
    sample_cols = ['pid', 'face_id', 'version', 'trust_rating', 'source_file']
    print(combined[sample_cols].head(10).to_string(index=False))
    
    # Show data by version
    print(f"\n📊 DATA BY VERSION:")
    version_counts = combined['version'].value_counts()
    for version, count in version_counts.items():
        print(f"  {version}: {count:,} responses")
    
    # Show data by face_id (first 10)
    print(f"\n🖼️  DATA BY FACE_ID (first 10):")
    face_counts = combined['face_id'].value_counts().head(10)
    for face_id, count in face_counts.items():
        print(f"  {face_id}: {count} responses")
    
    print(f"\n✅ ANALYSIS COMPLETE!")
    print(f"   Use '{output_file}' to verify the system is processing data correctly.")
    
    return combined

if __name__ == "__main__":
    analyze_test_data()
