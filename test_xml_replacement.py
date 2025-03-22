import os

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

# Print original XML for debugging
print("Original XML:")
print(test_xml)

# Write the original XML to a file
with open('original_test.xml', 'w', encoding='utf-8') as f:
    f.write(test_xml)

# Read the file content
with open('original_test.xml', 'r', encoding='utf-8') as f:
    xml_content = f.read()

# Do the string replacement
xml_with_name_tag = xml_content.replace("<n>", "<Name>").replace("</n>", "</Name>")

# Print the modified XML for debugging
print("\nModified XML:")
print(xml_with_name_tag)

# Write the modified XML to a different file
with open('fixed_test.xml', 'w', encoding='utf-8') as f:
    f.write(xml_with_name_tag)

# Verify by reading the file back
with open('fixed_test.xml', 'r', encoding='utf-8') as f:
    result = f.read()

# Check if Name tags are present
if "<Name>" in result and "</Name>" in result:
    print("\nSUCCESS: XML file has been fixed with proper <Name> tags")
    print(f"File was saved as: {os.path.abspath('fixed_test.xml')}")
else:
    print("\nERROR: Name tags were not correctly inserted!") 