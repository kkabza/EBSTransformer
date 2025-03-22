# Print what the tag looks like to confirm model processing
tag_name = "Name"
print(f"Tag name: {tag_name}")

# Create XML content with character representation
xml_str = '''<?xml version="1.0" encoding="UTF-8"?>
<Claim>
    <ClaimantInformation>
        <Claimant id="1">
            <''' + tag_name + '''>John Doe</''' + tag_name + '''>
            <Phone>123-456-7890</Phone>
        </Claimant>
    </ClaimantInformation>
</Claim>'''

# Print the XML string to see what it looks like
print("XML string:", xml_str)

# Write to file
with open("debug_tag_output.xml", "w", encoding="utf-8") as f:
    f.write(xml_str)

# Read back from file and print
with open("debug_tag_output.xml", "r", encoding="utf-8") as f:
    content = f.read()
    print("Content read from file:", content)

print("Script completed") 