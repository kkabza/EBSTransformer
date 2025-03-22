# Script to create a test XML file with Name tag
with open('test_with_name_tag.xml', 'w', encoding='utf-8') as f:
    f.write('''<?xml version="1.0" encoding="UTF-8"?>
<Claim>
    <ClaimDetails>
        <Value>123</Value>
    </ClaimDetails>
    <ClaimantInformation>
        <Claimant id="1">
            <Name>John Doe</Name>
            <Phone>123-456-7890</Phone>
        </Claimant>
    </ClaimantInformation>
</Claim>''')

print("File written with Name tag.") 