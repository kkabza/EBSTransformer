import xml.etree.ElementTree as ET
import xml.dom.minidom

# Create the root element
root = ET.Element("Claim")
root.set("version", "1.0")

# Create ClaimHeader
claim_header = ET.SubElement(root, "ClaimHeader")
ET.SubElement(claim_header, "ClaimNumber").text = "CL-12345-2023"
ET.SubElement(claim_header, "ClaimDate").text = "2023-05-15"
ET.SubElement(claim_header, "PolicyNumber").text = "POL-98765-2022"
ET.SubElement(claim_header, "InsuredName").text = "John Smith"

# Create ClaimDetails
claim_details = ET.SubElement(root, "ClaimDetails")
ET.SubElement(claim_details, "LossDate").text = "2023-05-10"
ET.SubElement(claim_details, "LossDescription").text = "Water damage due to burst pipe in kitchen"
loss_location = ET.SubElement(claim_details, "LossLocation")
ET.SubElement(loss_location, "Address1").text = "123 Main Street"
ET.SubElement(loss_location, "Address2").text = "Apt 4B"
ET.SubElement(loss_location, "City").text = "New York"
ET.SubElement(loss_location, "State").text = "NY"
ET.SubElement(loss_location, "ZipCode").text = "10001"
ET.SubElement(loss_location, "Country").text = "USA"

# Create ClaimantInformation
claimant_info = ET.SubElement(root, "ClaimantInformation")
claimant = ET.SubElement(claimant_info, "Claimant")
claimant.set("id", "CLM001")

# Explicitly create Name element and print it for debugging
name_elem = ET.SubElement(claimant, "Name")
name_elem.text = "John Smith"
print(f"Name element tag: {name_elem.tag}")

contact_info = ET.SubElement(claimant, "ContactInfo")
ET.SubElement(contact_info, "Phone").text = "212-555-1234"
ET.SubElement(contact_info, "Email").text = "john.smith@example.com"
ET.SubElement(claimant, "ClaimAmount").text = "5000.00"

# Create CoverageInformation
coverage_info = ET.SubElement(root, "CoverageInformation")
coverage1 = ET.SubElement(coverage_info, "Coverage")
coverage1.set("id", "COV001")
ET.SubElement(coverage1, "CoverageType").text = "Property Damage"
ET.SubElement(coverage1, "LimitAmount").text = "50000.00"
ET.SubElement(coverage1, "DeductibleAmount").text = "500.00"

coverage2 = ET.SubElement(coverage_info, "Coverage")
coverage2.set("id", "COV002")
ET.SubElement(coverage2, "CoverageType").text = "Personal Property"
ET.SubElement(coverage2, "LimitAmount").text = "25000.00"
ET.SubElement(coverage2, "DeductibleAmount").text = "250.00"

# Convert ElementTree to XML string with pretty format
xml_str = ET.tostring(root, encoding="utf-8").decode()
print(f"XML string before parsing: {xml_str}")
dom = xml.dom.minidom.parseString(xml_str)
pretty_xml = dom.toprettyxml(indent="    ")

# Add XML declaration manually
pretty_xml = '<?xml version="1.0" encoding="UTF-8"?>\n' + pretty_xml.split('\n', 1)[1]

# Write to file
with open("examples/sample_iso_claim.xml", "w", encoding="utf-8") as f:
    f.write(pretty_xml)

# Add direct string replacement as a fallback
with open("examples/sample_iso_claim.xml", "r", encoding="utf-8") as f:
    content = f.read()

content = content.replace("<n>", "<Name>").replace("</n>", "</Name>")

with open("examples/sample_iso_claim.xml", "w", encoding="utf-8") as f:
    f.write(content)

print("Sample ISO claim XML file created successfully with manual tag replacement.") 