"""
This script validates our understanding of the XML tags and XSLT transformation.
"""

import os
from lxml import etree
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Create sample XML with <n> tags
test_xml = """<?xml version="1.0" encoding="UTF-8"?>
<Claim>
    <ClaimHeader>
        <ClaimNumber>CL-12345-2023</ClaimNumber>
    </ClaimHeader>
    <ClaimantInformation>
        <Claimant id="CLM001">
            <n>John Smith</n>
            <ContactInfo>
                <Phone>212-555-1234</Phone>
            </ContactInfo>
        </Claimant>
    </ClaimantInformation>
</Claim>"""

# Save XML to a test file
test_xml_path = 'test_claim.xml'
with open(test_xml_path, 'w', encoding='utf-8') as f:
    f.write(test_xml)
    
logger.info(f"Created test XML file with <n> tags: {test_xml_path}")

# Try parsing the XML
try:
    xml_doc = etree.fromstring(test_xml.encode('utf-8'))
    logger.info("Successfully parsed XML content")
    
    # Check what the parsed <n> tag looks like
    n_elements = xml_doc.xpath('//n')
    if n_elements:
        logger.info(f"Found {len(n_elements)} <n> tag(s) in the parsed XML")
        for n_element in n_elements:
            logger.info(f"<n> tag content: {n_element.text}")
    else:
        logger.warning("No <n> tags found in the parsed XML")
    
except Exception as e:
    logger.error(f"Failed to parse XML: {str(e)}")

# Check if XSLT file exists and try to apply transformation
xslt_path = 'xslt/iso_claim.xslt'
if os.path.exists(xslt_path):
    try:
        # Parse the XSLT file
        xslt_doc = etree.parse(xslt_path)
        transform = etree.XSLT(xslt_doc)
        
        # Apply transformation
        result_tree = transform(xml_doc)
        transformed_xml = etree.tostring(result_tree, pretty_print=True, encoding='utf-8').decode('utf-8')
        
        logger.info("Successfully applied XSLT transformation")
        logger.info("Transformed XML: \n" + transformed_xml[:200] + "..." if len(transformed_xml) > 200 else transformed_xml)
        
    except Exception as e:
        logger.error(f"XSLT transformation failed: {str(e)}")
else:
    logger.warning(f"XSLT file not found: {xslt_path}")

# Cleanup
if os.path.exists(test_xml_path):
    os.remove(test_xml_path)
    logger.info(f"Removed test file: {test_xml_path}")

logger.info("Test completed successfully") 