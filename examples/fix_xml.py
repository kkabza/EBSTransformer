# Create a sample ISO claim XML file with Name tag correctly set
content = """<?xml version="1.0" encoding="UTF-8"?>
<Claim version="1.0">
    <ClaimHeader>
        <ClaimNumber>CL-12345-2023</ClaimNumber>
        <ClaimDate>2023-05-15</ClaimDate>
        <PolicyNumber>POL-98765-2022</PolicyNumber>
        <InsuredName>John Smith</InsuredName>
    </ClaimHeader>
    <ClaimDetails>
        <LossDate>2023-05-10</LossDate>
        <LossDescription>Water damage due to burst pipe in kitchen</LossDescription>
        <LossLocation>
            <Address1>123 Main Street</Address1>
            <Address2>Apt 4B</Address2>
            <City>New York</City>
            <State>NY</State>
            <ZipCode>10001</ZipCode>
            <Country>USA</Country>
        </LossLocation>
    </ClaimDetails>
    <ClaimantInformation>
        <Claimant id="CLM001">
            <Name>John Smith</Name>
            <ContactInfo>
                <Phone>212-555-1234</Phone>
                <Email>john.smith@example.com</Email>
            </ContactInfo>
            <ClaimAmount>5000.00</ClaimAmount>
        </Claimant>
    </ClaimantInformation>
    <CoverageInformation>
        <Coverage id="COV001">
            <CoverageType>Property Damage</CoverageType>
            <LimitAmount>50000.00</LimitAmount>
            <DeductibleAmount>500.00</DeductibleAmount>
        </Coverage>
        <Coverage id="COV002">
            <CoverageType>Personal Property</CoverageType>
            <LimitAmount>25000.00</LimitAmount>
            <DeductibleAmount>250.00</DeductibleAmount>
        </Coverage>
    </CoverageInformation>
</Claim>"""

with open("examples/sample_iso_claim.xml", "w", encoding="utf-8") as f:
    f.write(content)

print("Fixed XML file created successfully.") 