import re

def format_tag_if_needed(xml_content):
    """
    Replace <n> tags with <Name> tags and </n> tags with </Name> tags in XML content.
    This function uses regex to find and replace the tags.
    """
    # Print for debugging
    print("Original XML content:", xml_content)
    
    # Use string replacement instead of regex to avoid issues
    result = xml_content.replace("<n>", "<Name>").replace("</n>", "</Name>")
    
    # Print for debugging
    print("Modified XML content:", result)
    
    return result

# Create a test XML file with <n> tag
test_xml = '''<?xml version="1.0" encoding="UTF-8"?>
<Claim>
    <ClaimantInformation>
        <Claimant id="1">
            <n>John Doe</n>
            <Phone>123-456-7890</Phone>
        </Claimant>
    </ClaimantInformation>
</Claim>'''

print("Test XML with <n> tag:", test_xml)

# Apply the tag replacement
fixed_xml = format_tag_if_needed(test_xml)

print("Fixed XML with <Name> tag:", fixed_xml)

# Write the result to a file
with open('test_name_output.xml', 'w', encoding='utf-8') as f:
    f.write(fixed_xml)

print("Fixed XML written to test_name_output.xml")

# Now read back the file to verify
with open('test_name_output.xml', 'r', encoding='utf-8') as f:
    file_content = f.read()
    
print("Content read from file:", file_content)

# Verify that the tag was replaced correctly
if "<Name>" in file_content and "</Name>" in file_content:
    print("SUCCESS: <Name> tags are in the file")
else:
    print("ERROR: <Name> tags not found in the file") 