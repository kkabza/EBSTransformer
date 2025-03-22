import csv
import os

# Create output directory if it doesn't exist
output_dir = 'individual_claims'
os.makedirs(output_dir, exist_ok=True)

# Read the detailed samples CSV file
input_file = 'examples/safelite_detailed_samples.csv'

with open(input_file, 'r', encoding='utf-8') as f:
    reader = csv.reader(f)
    header = next(reader)  # Get the header row
    
    # Process each row (claim)
    for i, row in enumerate(reader, 1):
        # Create individual file name with claim number
        claim_number = row[0]
        output_file = os.path.join(output_dir, f'{claim_number}.csv')
        
        # Write the header and the single row to a new file
        with open(output_file, 'w', encoding='utf-8', newline='') as out_f:
            writer = csv.writer(out_f)
            writer.writerow(header)
            writer.writerow(row)
        
        print(f"Created file {i}: {output_file}")

# Handle the original sample file if it exists
sample_file = 'examples/sample_safelite_claims.csv'
if os.path.exists(sample_file):
    with open(sample_file, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        header = next(reader)  # Get the header row
        
        # Process each row (claim)
        for row in reader:
            # Create individual file name with claim number
            claim_number = row[0]
            output_file = os.path.join(output_dir, f'{claim_number}.csv')
            
            # Only create if doesn't already exist
            if not os.path.exists(output_file):
                # Write the header and the single row to a new file
                with open(output_file, 'w', encoding='utf-8', newline='') as out_f:
                    writer = csv.writer(out_f)
                    writer.writerow(header)
                    writer.writerow(row)
                
                print(f"Created file from sample: {output_file}")

print(f"Completed creating individual claim files in {output_dir}/") 