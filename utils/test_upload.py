"""
Test script to upload an XML file to the transformation service.
"""
import requests
import sys
import os
import json
import time

def test_upload(file_path):
    """Upload a file to the transformation service and print the result."""
    url = "http://localhost:5000/upload"
    
    if not os.path.exists(file_path):
        print(f"Error: File {file_path} not found")
        return
    
    print(f"Uploading file: {file_path}")
    
    with open(file_path, 'rb') as f:
        files = {'file': (os.path.basename(file_path), f, 'text/xml')}
        response = requests.post(url, files=files)
    
    print(f"Status code: {response.status_code}")
    print("Response headers:")
    print(json.dumps(dict(response.headers), indent=4))
    print("\nResponse body:")
    print(response.text)
    
    # If successful, get the result_id and check status
    if response.status_code == 200:
        try:
            result = response.json()
            result_id = result.get('result_id')
            if result_id:
                print(f"\nChecking status for result_id: {result_id}")
                check_status_and_result(result_id)
        except json.JSONDecodeError:
            print("Could not parse JSON response")

def check_status_and_result(result_id):
    """Check the status and then get the result if processing is complete."""
    status_url = f"http://localhost:5000/status/{result_id}"
    
    # Check status more times with longer waiting periods
    for i in range(20):  # Increased from 5 to 20 attempts
        response = requests.get(status_url)
        print(f"Status check #{i+1} - Status code: {response.status_code}")
        
        try:
            status = response.json()
            print(f"Status: {status}")
            
            if status.get('status') == 'completed':
                get_result(result_id)
                break
            
            # Wait before next check, increasing the wait time
            wait_time = 2 + i  # Start with 2 seconds, then increase
            print(f"Waiting {wait_time} seconds before next check...")
            time.sleep(wait_time)
        except json.JSONDecodeError:
            print("Could not parse JSON status response")
            break

def get_result(result_id):
    """Get the transformation result."""
    result_url = f"http://localhost:5000/result/{result_id}"
    response = requests.get(result_url)
    
    print(f"\nResult - Status code: {response.status_code}")
    print("Result response:")
    print(response.text)

if __name__ == "__main__":
    file_path = "examples/sample_iso_claim.xml"
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
    
    test_upload(file_path) 