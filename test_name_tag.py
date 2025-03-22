import re

def format_tag_if_needed(xml_content):
    """
    Format XML content by replacing <n> tags with <Name> tags.
    """
    # Simple direct string replacement
    formatted_content = xml_content.replace("<n>", "<Name>").replace("</n>", "</Name>")
    print(f"After replacement: {formatted_content}")
    return formatted_content

# Test with a simple XML
test_xml = """<?xml version="1.0" encoding="UTF-8"?>
<Claim>
    <ClaimDetails>
        <Value>123</Value>
    </ClaimDetails>
    <ClaimantInformation>
        <Claimant id="1">
            <n>John Doe</n>
            <Phone>123-456-7890</Phone>
        </Claimant>
    </ClaimantInformation>
</Claim>"""

print("Original XML:")
print(test_xml)

result = format_tag_if_needed(test_xml)

print("\nResult of replacement:")
print(result)

# Write to file to verify
with open("test_output.xml", "w", encoding="utf-8") as f:
    f.write(result)

print("\nFile written - now reading it back:")
with open("test_output.xml", "r", encoding="utf-8") as f:
    content = f.read()
    print(content) 