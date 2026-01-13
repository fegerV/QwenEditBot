#!/usr/bin/env python3
"""
Script to get the current ngrok public URL
"""

import requests
import json

def get_ngrok_url():
    """
    Get the public URL from ngrok's API
    Assumes ngrok is running and accessible at localhost:4040
    """
    try:
        response = requests.get('http://localhost:4040/api/tunnels')
        data = response.json()
        
        # Find the HTTPS tunnel for port 800
        for tunnel in data['tunnels']:
            if tunnel['proto'] == 'https' and ':8000' in tunnel['config']['addr']:
                return tunnel['public_url']
        
        # If no specific port 8000 tunnel found, return the first HTTPS tunnel
        for tunnel in data['tunnels']:
            if tunnel['proto'] == 'https':
                return tunnel['public_url']
                
    except Exception as e:
        print(f"Could not retrieve ngrok URL: {e}")
        print("This likely means ngrok is not currently running.")
        print("To start ngrok, run: start_system_ngrok.bat")
        return None

if __name__ == "__main__":
    url = get_ngrok_url()
    if url:
        print(f"Current ngrok public URL: {url}")
        print(f"For Telegram webhook, use: {url}/api/telegram/webhook")
    else:
        print("No ngrok tunnel found. Please start ngrok first.")