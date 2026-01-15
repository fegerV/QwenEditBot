#!/usr/bin/env python3
"""
Simple test to verify bot can connect to backend
"""

import asyncio
import sys
from pathlib import Path

# Add project paths
sys.path.insert(0, str(Path(__file__).parent / 'bot'))

from bot.services.api_client import BackendAPIClient

async def test_connection():
    """Test basic connection between bot and backend"""
    print("Testing bot-backend connection...")
    
    try:
        client = BackendAPIClient()
        print(f"Client created successfully with base URL: {client.base_url}")
        
        # Test health endpoint
        response = await client._request('GET', '/health')
        print(f"Health check response: {response}")
        
        # Test root endpoint
        response = await client._request('GET', '/')
        print(f"Root endpoint response: {response}")
        
        print("✅ Connection test passed!")
        return True
        
    except Exception as e:
        print(f"❌ Connection test failed: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_connection())
    if success:
        print("\nBot can successfully connect to the backend!")
    else:
        print("\nBot failed to connect to the backend.")
        sys.exit(1)