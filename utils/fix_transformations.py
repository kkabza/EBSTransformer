#!/usr/bin/env python
"""
Fix transformation results that have XML validation issues.
This tool can be used to fix specific transformation results that failed XML validation.
"""
import os
import re
import sys
import xml.etree.ElementTree as ET
from datetime import datetime

def is_valid_xml(xml_content):
    """Check if XML content is valid"""
    try:
        ET.fromstring(xml_content)
        return True
    except ET.ParseError as e:
        print(f"XML Validation Error: {e}")
        return False

def extract_xml_from_markdown(content):
    """Extract XML content from markdown code blocks"""
    xml_pattern = re.compile(r'```(?:xml)?\s*([\s\S]*?)```')
    markdown_match = xml_pattern.search(content)
    
    if markdown_match:
        xml_content = markdown_match.group(1).strip()
        print(f"Extracted XML from markdown, length: {len(xml_content)} characters")
        return xml_content
    
    return content

def fix_customer_name_tags(xml_content):
    """Fix Customer/Name element structure"""
    if '<Customer>' in xml_content and '<n>' in xml_content:
        fixed_content = xml_content.replace('<n>', '<Name>').replace('</n>', '</Name>')
        print("Fixed Customer/Name element structure")
        return fixed_content
    return xml_content

def fix_safelite_structure(xml_content):
    """Ensure proper structure for Safelite claims"""
    # First fix name tags
    xml_content = fix_customer_name_tags(xml_content)
    
    # Check if we need to add the proper root elements
    if not xml_content.strip().startswith('<?xml') and not xml_content.strip().startswith('<SafeliteClaimsBatch'):
        # If it has Claims or Claim elements
        if '<Claims>' in xml_content or '<Claim>' in xml_content:
            batch_id = f"SFB{datetime.now().strftime('%Y%m%d%H%M%S')}"
            claims_count = xml_content.count('<Claim>')
            
            # Add Claims wrapper if needed
            if '<Claims>' not in xml_content and '<Claim>' in xml_content:
                xml_content = f"<Claims>\n{xml_content}\n</Claims>"
                print("Added <Claims> wrapper")
            
            # Add SafeliteClaimsBatch wrapper
            xml_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<SafeliteClaimsBatch>
    <BatchInfo>
        <BatchId>{batch_id}</BatchId>
        <GeneratedDate>{datetime.now().isoformat()}</GeneratedDate>
        <ClaimCount>{claims_count}</ClaimCount>
    </BatchInfo>
    {xml_content}
</SafeliteClaimsBatch>"""
            print("Added SafeliteClaimsBatch structure")
    
    return xml_content

def fix_result_file(result_id):
    """Fix the transformation result file for a specific result_id"""
    # Construct the file paths
    result_file = f"uploads/{result_id}_result.txt"
    fixed_file = f"uploads/{result_id}_fixed.xml"
    
    if not os.path.exists(result_file):
        print(f"Error: Result file not found: {result_file}")
        return False
    
    # Read the content
    with open(result_file, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Extract the XML from markdown if needed
    xml_content = extract_xml_from_markdown(content)
    
    # Fix the structure
    fixed_content = fix_safelite_structure(xml_content)
    
    # Validate the result
    if is_valid_xml(fixed_content):
        print("XML is now valid!")
        # Save the fixed content
        with open(fixed_file, 'w', encoding='utf-8') as file:
            file.write(fixed_content)
        print(f"Fixed XML saved to: {fixed_file}")
        return True
    else:
        print("Failed to fix XML structure")
        return False

def main():
    if len(sys.argv) < 2:
        print("Usage: python fix_transformations.py <result_id>")
        return
    
    result_id = sys.argv[1]
    if fix_result_file(result_id):
        print(f"Successfully fixed result for {result_id}")
    else:
        print(f"Failed to fix result for {result_id}")

if __name__ == "__main__":
    main() 
