#!/usr/bin/env python
"""
Quick script to fix a specific transformation result
"""
import re
import os
import xml.etree.ElementTree as ET
from datetime import datetime

# Specific result ID to fix
RESULT_ID = 'f896e5e7-436e-41b3-90c9-7405eb6a5299'
INPUT_FILE = f'uploads/{RESULT_ID}_result.txt'
OUTPUT_FILE = f'uploads/{RESULT_ID}_fixed.xml'

def main():
    # Check if file exists
    if not os.path.exists(INPUT_FILE):
        print(f"Error: File not found: {INPUT_FILE}")
        return
    
    # Read the content
    with open(INPUT_FILE, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Extract XML from markdown code blocks if present
    xml_pattern = re.compile(r'```(?:xml)?\s*([\s\S]*?)```')
    markdown_match = xml_pattern.search(content)
    
    if markdown_match:
        xml_content = markdown_match.group(1).strip()
        print(f"Extracted XML from markdown, length: {len(xml_content)} characters")
    else:
        xml_content = content
        print(f"Using original content, length: {len(xml_content)} characters")
    
    # Creating proper XML structure for Safelite claims
    batch_id = f"SFB{datetime.now().strftime('%Y%m%d%H%M%S')}"
    claims_count = xml_content.count('<Claim>')
    
    # Wrap in proper structure if needed
    if '<Claims>' not in xml_content and '<Claim>' in xml_content:
        xml_content = f"<Claims>\n{xml_content}\n</Claims>"
        print("Added <Claims> wrapper")
    
    # Create full SafeliteClaimsBatch structure
    fixed_xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<SafeliteClaimsBatch>
    <BatchInfo>
        <BatchId>{batch_id}</BatchId>
        <GeneratedDate>{datetime.now().isoformat()}</GeneratedDate>
        <ClaimCount>{claims_count}</ClaimCount>
    </BatchInfo>
    {xml_content}
</SafeliteClaimsBatch>"""
    
    # Validate the XML
    try:
        ET.fromstring(fixed_xml)
        print("XML is valid!")
        
        # Save the fixed content
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as file:
            file.write(fixed_xml)
        
        print(f"Fixed XML saved to: {OUTPUT_FILE}")
    except ET.ParseError as e:
        print(f"XML is still invalid: {e}")
        
        # Save anyway for debugging
        debug_file = f'uploads/{RESULT_ID}_debug.xml'
        with open(debug_file, 'w', encoding='utf-8') as file:
            file.write(fixed_xml)
        
        print(f"Debug XML saved to: {debug_file}")

if __name__ == "__main__":
    main() 