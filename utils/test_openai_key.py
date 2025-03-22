"""
Test script to check if the OpenAI API key is being loaded correctly.
"""
import os
from dotenv import load_dotenv

def check_openai_key():
    """Check if the OpenAI API key is loaded correctly from .env file."""
    print("Before load_dotenv():")
    print(f"OPENAI_API_KEY in environment: {'OPENAI_API_KEY' in os.environ}")
    
    # Attempt to load environment variables from .env
    loaded = load_dotenv(verbose=True)
    print(f"\nload_dotenv() result: {loaded}")
    
    print("\nAfter load_dotenv():")
    print(f"OPENAI_API_KEY in environment: {'OPENAI_API_KEY' in os.environ}")
    
    # Check if the OPENAI_API_KEY is set
    api_key = os.environ.get('OPENAI_API_KEY')
    
    print("\nOpenAI API Key Check:")
    if api_key:
        # Mask the key for security (show only a few characters)
        masked_key = f"{api_key[:8]}...{api_key[-4:]}" if len(api_key) > 12 else "***KEY TOO SHORT***"
        print(f"✓ OPENAI_API_KEY is set: {masked_key}")
        
        # Validate key format (starts with 'sk-')
        if api_key.startswith('sk-'):
            print("✓ Key format appears valid (starts with 'sk-')")
        else:
            print("✗ Key format appears invalid (should start with 'sk-')")
    else:
        print("✗ OPENAI_API_KEY is not set")
    
    # Try to read the content of the .env file directly
    print("\nAttempting to read .env file directly:")
    try:
        if os.path.exists('.env'):
            with open('.env', 'r') as f:
                env_content = f.read()
                print("✓ .env file exists and contains:")
                for line in env_content.split('\n'):
                    if line.strip() and not line.startswith('#'):
                        if 'OPENAI_API_KEY' in line:
                            key_part = line.split('=', 1)[1] if '=' in line else "No value"
                            if len(key_part) > 12:
                                masked = f"{key_part[:8]}...{key_part[-4:]}"
                            else:
                                masked = "***VALUE TOO SHORT***"
                            print(f"  - OPENAI_API_KEY={masked}")
                        else:
                            print(f"  - {line}")
        else:
            print("✗ .env file does not exist")
    except Exception as e:
        print(f"✗ Error reading .env file: {str(e)}")

if __name__ == "__main__":
    check_openai_key() 