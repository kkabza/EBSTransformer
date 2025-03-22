# Creating a workaround to generate XML with proper Name tag
# We'll use individual character assembly to bypass the model's replacement

tag_start = '<'
tag_end = '>'
slash = '/'
# Define the letters for our tag name
n_char = 'N'
a_char = 'a'
m_char = 'm'
e_char = 'e'
tag_name = n_char + a_char + m_char + e_char  # This spells "Name"

# Print debug info
print(f"Tag name characters: {n_char}+{a_char}+{m_char}+{e_char} = {tag_name}")

# Assemble the opening and closing tags
opening_tag = tag_start + tag_name + tag_end
closing_tag = tag_start + slash + tag_name + tag_end

print(f"Opening tag: {opening_tag}")
print(f"Closing tag: {closing_tag}")

# Build the XML
xml_str = f'''<?xml version="1.0" encoding="UTF-8"?>
<Claim>
    <ClaimantInformation>
        <Claimant id="1">
            {opening_tag}John Doe{closing_tag}
            <Phone>123-456-7890</Phone>
        </Claimant>
    </ClaimantInformation>
</Claim>'''

print("XML string:", xml_str)

# Write to file
with open("workaround_output.xml", "w", encoding="utf-8") as f:
    f.write(xml_str)

# Read back from file and print
with open("workaround_output.xml", "r", encoding="utf-8") as f:
    content = f.read()
    print("Content read from file:", content)

# Check if our tag survived
if f"{opening_tag}John Doe{closing_tag}" in content:
    print(f"SUCCESS: The tag {opening_tag}...{closing_tag} was preserved in the file")
else:
    print("ERROR: The tag was changed in the file") 