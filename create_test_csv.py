import os
import csv

# Create responses directory if it doesn't exist
responses_dir = os.path.join(os.getcwd(), 'data', 'responses')
os.makedirs(responses_dir, exist_ok=True)

# Define test data
test_data = [
    {
        'Participant ID': '101',
        'Trust': '4',
        'Emotion': '3',
        'Face': 'face1.jpg',
        'FaceVersion': 'Full Face'
    },
    {
        'Participant ID': '101',
        'Trust': '5',
        'Emotion': '4',
        'Face': 'face2.jpg',
        'FaceVersion': 'Left Half'
    },
    {
        'Participant ID': '101',
        'Trust': '3',
        'Emotion': '2',
        'Face': 'face3.jpg',
        'FaceVersion': 'Right Half'
    }
]

# Write to CSV file
csv_path = os.path.join(responses_dir, 'test_participant.csv')
with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
    fieldnames = ['Participant ID', 'Trust', 'Emotion', 'Face', 'FaceVersion']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    
    writer.writeheader()
    for row in test_data:
        writer.writerow(row)

print(f"Created test CSV file at: {csv_path}")

# Output the contents for verification
print("\nCSV Contents:")
with open(csv_path, 'r', encoding='utf-8') as csvfile:
    print(csvfile.read())
