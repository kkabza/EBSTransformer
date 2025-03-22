#!/usr/bin/env python
"""
Fix XML validation issues in transformation results.
This script extracts XML content from markdown-formatted responses and ensures
proper structure for Safelite claims.
"""
import re
import sys
import os
from datetime import datetime
import xml.etree.ElementTree as ET

def extract_xml_from_markdown(content):
    """Extract XML content from markdown code blocks"""
    xml_pattern = re.compile(r'```(?:xml)?\s*([\s\S]*?)```')
    markdown_match = xml_pattern.search(content)
    
    if markdown_match:
        return markdown_match.group(1).strip()
    return content

def is_valid_xml(xml_content):
    """Check if XML content is valid"""
    try:
        ET.fromstring(xml_content)
        return True
    except ET.ParseError:
        return False

def fix_safelite_structure(xml_content):
    """Ensure proper structure for Safelite claims"""
    # Fix Customer/Name structure
    if '<Customer>' in xml_content and '<n>' in xml_content:
        xml_content = xml_content.replace('<n>', '<Name>').replace('</n>', '</Name>')
        print("Fixed Customer/Name element structure")
    
    # If the XML is missing the SafeliteClaimsBatch root element
    if not xml_content.strip().startswith('<?xml') and not xml_content.strip().startswith('<SafeliteClaimsBatch'):
        
        # If it's just Claims or Claim elements, wrap it properly
        if '<Claims>' in xml_content or '<Claim>' in xml_content:
            batch_id = f"SFB{datetime.now().strftime('%Y%m%d%H%M%S')}"
            claims_count = xml_content.count('<Claim>')
            
            # If we have only Claim elements but no Claims wrapper
            if '<Claims>' not in xml_content and '<Claim>' in xml_content:
                xml_content = f"<Claims>\n{xml_content}\n</Claims>"
            
            # Now wrap in SafeliteClaimsBatch
            xml_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<SafeliteClaimsBatch>
    <BatchInfo>
        <BatchId>{batch_id}</BatchId>
        <GeneratedDate>{datetime.now().isoformat()}</GeneratedDate>
        <ClaimCount>{claims_count}</ClaimCount>
    </BatchInfo>
    {xml_content}
</SafeliteClaimsBatch>"""
            
            print(f"Enhanced XML structure for Safelite format")
    
    return xml_content

def main():
    """Main function to fix XML validation issues"""
    if len(sys.argv) < 2:
        print("Usage: python fix_xml.py <file_path>")
        return
    
    file_path = sys.argv[1]
    
    if not os.path.exists(file_path):
        print(f"Error: File not found: {file_path}")
        return
    
    # Read the file content
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Extract XML content from markdown
    xml_content = extract_xml_from_markdown(content)
    
    # Fix Safelite structure
    xml_content = fix_safelite_structure(xml_content)
    
    # Check if the result is valid XML
    if is_valid_xml(xml_content):
        print("XML is valid")
        
        # Save the result with _fixed suffix
        output_path = os.path.splitext(file_path)[0] + "_fixed.xml"
        with open(output_path, 'w', encoding='utf-8') as file:
            file.write(xml_content)
        
        print(f"Fixed XML saved to: {output_path}")
    else:
        print("Error: XML is still not valid after fixing")
        
        # Save the result anyway for debugging
        output_path = os.path.splitext(file_path)[0] + "_attempted_fix.xml"
        with open(output_path, 'w', encoding='utf-8') as file:
            file.write(xml_content)
        
        print(f"Attempted fix saved to: {output_path}")

if __name__ == "__main__":
    main() 
