import csv
import os
import shutil

# Create/clear output directory
output_dir = 'individual_claims'
if os.path.exists(output_dir):
    shutil.rmtree(output_dir)
os.makedirs(output_dir)

# Read the detailed samples CSV file
input_file = 'examples/safelite_detailed_samples.csv'

with open(input_file, 'r', encoding='utf-8') as f:
    reader = csv.reader(f)
    header = next(reader)  # Get the header row
    rows = list(reader)

# Get first 50 rows for individual files
rows_to_use = rows[:50]
    
# Process each row (claim) up to 50
for i, row in enumerate(rows_to_use, 1):
    # Create individual file name with claim number
    claim_number = row[0]
    output_file = os.path.join(output_dir, f'{claim_number}.csv')
    
    # Write the header and the single row to a new file
    with open(output_file, 'w', encoding='utf-8', newline='') as out_f:
        writer = csv.writer(out_f)
        writer.writerow(header)
        writer.writerow(row)
    
    print(f"Created file {i}/50: {output_file}")

# Count final files
file_count = len(os.listdir(output_dir))
print(f"Completed creating {file_count} individual claim files in {output_dir}/")

# Verify count
if file_count != 50:
    print(f"WARNING: Expected 50 files but found {file_count}")
else:
    print("SUCCESS: Exactly 50 files were created as requested.") 