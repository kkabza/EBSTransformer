# This script demonstrates the XML tag replacement function
import re

def n_to_name_tag(xml_content):
    """This function replaces <n> tags with <Name> tags at runtime."""
    print("Input XML:", xml_content)
    
    # Create variables for the replacement strings
    n_open = "<n>"
    n_close = "</n>"
    name_open = "<Name>"
    name_close = "</Name>"
    
    # Print the variables to verify what they contain
    print(f"Replacing: '{n_open}' with '{name_open}'")
    print(f"Replacing: '{n_close}' with '{name_close}'")
    
    # Perform the replacements
    result = xml_content.replace(n_open, name_open)
    result = result.replace(n_close, name_close)
    
    print("Output XML:", result)
    return result

# Create a test XML string
test_xml = """<?xml version="1.0" encoding="UTF-8"?>
<Claim>
    <ClaimantInformation>
        <Claimant id="1">
            <n>John Doe</n>
            <Phone>123-456-7890</Phone>
        </Claimant>
    </ClaimantInformation>
</Claim>"""

# Apply the function
fixed_xml = n_to_name_tag(test_xml)

# Save to a file
with open("fixed_name_tag.xml", "w", encoding="utf-8") as f:
    f.write(fixed_xml)

print(f"\nResults saved to fixed_name_tag.xml")

# Verify by reading back the file
with open("fixed_name_tag.xml", "r", encoding="utf-8") as f:
    file_content = f.read()

# Check if the name tag exists in the output
if "<Name>" in file_content:
    print("SUCCESS: <Name> tag was found in the output file")
else:
    print("FAIL: <Name> tag was not found in the output file") 