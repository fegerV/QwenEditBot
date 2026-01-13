import asyncio
import aiohttp
import sys
from pathlib import Path

# Add the worker directory to the path so we can import the config
sys.path.insert(0, str(Path(__file__).parent / 'worker'))

from worker.config import settings

async def test_comfyui_connection():
    """
    Test connection to ComfyUI by checking its health endpoint
    """
    print(f"Testing connection to ComfyUI at: {settings.COMFYUI_URL}")
    
    async with aiohttp.ClientSession() as session:
        try:
            # Test basic connectivity by accessing the system_stats endpoint
            async with session.get(
                f"{settings.COMFYUI_URL}/system_stats",
                timeout=aiohttp.ClientTimeout(total=10)
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"[SUCCESS] Successfully connected to ComfyUI!")
                    print(f"  Status: {response.status}")
                    print(f"  Response: {data}")
                    return True
                else:
                    print(f"[ERROR] Connection failed with status: {response.status}")
                    error_text = await response.text()
                    print(f"  Error: {error_text}")
                    return False
        except asyncio.TimeoutError:
            print("[ERROR] Connection timed out. Is ComfyUI running?")
            return False
        except aiohttp.ClientConnectorError as e:
            print(f"[ERROR] Cannot connect to ComfyUI: {e}")
            print("  Please check if ComfyUI is running on the configured port.")
            return False
        except Exception as e:
            print(f"[ERROR] Unexpected error connecting to ComfyUI: {e}")
            return False

async def test_all_comfyui_endpoints():
    """
    Test various ComfyUI endpoints to verify full functionality
    """
    endpoints_to_test = [
        "/system_stats",
        "/object_info",
        "/prompt",
        "/queue",
        "/history"
    ]
    
    print("\nTesting individual ComfyUI endpoints:")
    print("=" * 50)
    
    async with aiohttp.ClientSession() as session:
        for endpoint in endpoints_to_test:
            try:
                async with session.get(
                    f"{settings.COMFYUI_URL}{endpoint}",
                    timeout=aiohttp.ClientTimeout(total=5)
                ) as response:
                    status_icon = "[OK]" if response.status in [200, 404, 405] else "[FAIL]"
                    print(f"{status_icon} {endpoint}: {response.status}")
                    
                    # For some endpoints that expect POST, 405 is normal
                    if response.status == 405:  # Method not allowed
                        print(f"  Note: {endpoint} expects POST request (normal)")
                        
            except Exception as e:
                print(f"[FAIL] {endpoint}: Failed to reach ({e})")

if __name__ == "__main__":
    print("ComfyUI Connection Test")
    print("=" * 50)
    
    # Run the main connection test
    connection_success = asyncio.run(test_comfyui_connection())
    
    if connection_success:
        # If basic connection works, test all endpoints
        asyncio.run(test_all_comfyui_endpoints())
    
    print("\nTest completed.")