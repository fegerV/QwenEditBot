import requests
import subprocess
import sys
import time

def check_backend():
    try:
        response = requests.get('http://localhost:8000/health', timeout=5)
        return response.status_code == 200
    except:
        return False

def main():
    print("Verifying services after restart...")
    
    # Check if backend is responding
    print("Checking backend service...", end="")
    if check_backend():
        print(" OK")
    else:
        print(" FAILED")
        print("Backend service might not be fully started yet.")
        return 1
    
    print("Services verification completed successfully!")
    return 0

if __name__ == "__main__":
    sys.exit(main())