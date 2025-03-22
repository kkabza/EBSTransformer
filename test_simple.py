"""
Simple test script to check if the application is working correctly.
"""
import requests
import os
import sys
import json
import time

def check_app_status():
    """Check if the application is running and its endpoints are accessible."""
    base_url = "http://localhost:5000"
    
    # Check home page
    try:
        response = requests.get(base_url)
        print(f"Home page status: {response.status_code}")
        print(f"Content-Type: {response.headers.get('Content-Type')}")
        if response.status_code == 200:
            print("Home page is accessible ✓")
        else:
            print(f"Home page returned status code: {response.status_code} ✗")
    except requests.exceptions.RequestException as e:
        print(f"Error accessing home page: {e} ✗")
    
    # Check metrics endpoint
    try:
        response = requests.get(f"{base_url}/metrics")
        print(f"\nMetrics endpoint status: {response.status_code}")
        if response.status_code == 200:
            print("Metrics endpoint is accessible ✓")
        else:
            print(f"Metrics endpoint returned status code: {response.status_code} ✗")
    except requests.exceptions.RequestException as e:
        print(f"Error accessing metrics endpoint: {e} ✗")
    
    # List available test files
    print("\nAvailable test files:")
    examples_dir = "examples"
    if os.path.exists(examples_dir) and os.path.isdir(examples_dir):
        xml_files = [f for f in os.listdir(examples_dir) if f.endswith(".xml")]
        for i, file in enumerate(xml_files, 1):
            print(f"{i}. {file}")
        
        if xml_files:
            print("\nTo test file upload, run this script with a file number:")
            print("python test_simple.py <file_number>")
            
            # If a file number was provided, test the upload
            if len(sys.argv) > 1:
                try:
                    file_num = int(sys.argv[1])
                    if 1 <= file_num <= len(xml_files):
                        test_file = os.path.join(examples_dir, xml_files[file_num-1])
                        print(f"\nTesting upload with file: {test_file}")
                        test_upload(test_file)
                    else:
                        print(f"Invalid file number. Please choose 1-{len(xml_files)}")
                except ValueError:
                    print("Please provide a valid file number")
    else:
        print(f"Examples directory '{examples_dir}' not found ✗")

def test_upload(file_path):
    """Test uploading a file to the application."""
    base_url = "http://localhost:5000"
    upload_url = f"{base_url}/upload"
    
    try:
        with open(file_path, 'rb') as f:
            files = {'file': (os.path.basename(file_path), f, 'text/xml')}
            response = requests.post(upload_url, files=files)
        
        print(f"Upload status: {response.status_code}")
        if response.status_code == 200:
            print("File upload successful ✓")
            print(f"Response: {response.text}")
            
            try:
                result = response.json()
                result_id = result.get('result_id')
                if result_id:
                    print(f"\nResult ID: {result_id}")
                    check_transformation_status(base_url, result_id)
                else:
                    print("No result_id in response ✗")
            except json.JSONDecodeError:
                print("Could not parse JSON response ✗")
        else:
            print(f"File upload failed with status code: {response.status_code} ✗")
            print(f"Response: {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"Error uploading file: {e} ✗")
    except Exception as e:
        print(f"Unexpected error: {e} ✗")

def check_transformation_status(base_url, result_id):
    """Check the status of a transformation and get the result if available."""
    status_url = f"{base_url}/status/{result_id}"
    max_checks = 10
    
    print("\nChecking transformation status...")
    for i in range(max_checks):
        try:
            response = requests.get(status_url)
            if response.status_code == 200:
                status_data = response.json()
                status = status_data.get('status')
                print(f"Check #{i+1}: Status = {status}")
                
                if status == 'completed':
                    print("Transformation completed ✓")
                    get_transformation_result(base_url, result_id)
                    return
                elif status == 'failed':
                    print("Transformation failed ✗")
                    return
                
                # Wait before next check
                wait_time = 2
                print(f"Waiting {wait_time} seconds...")
                time.sleep(wait_time)
            else:
                print(f"Status check failed with status code: {response.status_code} ✗")
                return
        except requests.exceptions.RequestException as e:
            print(f"Error checking status: {e} ✗")
            return
        except Exception as e:
            print(f"Unexpected error: {e} ✗")
            return
    
    print(f"Transformation still pending after {max_checks} checks")

def get_transformation_result(base_url, result_id):
    """Get the result of a completed transformation."""
    result_url = f"{base_url}/result/{result_id}"
    
    try:
        response = requests.get(result_url)
        print(f"\nResult status: {response.status_code}")
        if response.status_code == 200:
            print("Got transformation result ✓")
            print("\nTransformation result:")
            print(response.text)
        else:
            print(f"Failed to get result with status code: {response.status_code} ✗")
            print(f"Response: {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"Error getting result: {e} ✗")
    except Exception as e:
        print(f"Unexpected error: {e} ✗")

if __name__ == "__main__":
    check_app_status() 