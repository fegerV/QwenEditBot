"""Test script to verify sending prompts to ComfyUI API"""

import asyncio
import json
import aiohttp
import sys
import os
from pathlib import Path

# Add the project root to the Python path to allow imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from worker.config import settings
from worker.workflows.qwen_edit_2511 import build_workflow
from worker.job_queue.job_queue import Job


async def test_send_prompt():
    """Test sending a prompt directly to ComfyUI API"""
    print("Testing prompt sending to ComfyUI API...")
    
    # Create a mock job for testing
    from datetime import datetime
    
    test_job = Job(
        id=999999,
        user_id=1,
        image_path="test_image.jpg",  # This will be used to form the input filename
        prompt="Convert to comic style",
        status="queued",
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    
    # Build workflow using the same function that the worker uses
    workflow = build_workflow(test_job)
    
    print(f"Built workflow for job {test_job.id}")
    
    # Send the workflow to ComfyUI API
    url = f"{settings.COMFYUI_URL}/prompt"
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=workflow) as response:
                if response.status == 200:
                    data = await response.json()
                    prompt_id = data.get("prompt_id")
                    
                    if prompt_id:
                        print(f"V Successfully sent prompt to ComfyUI")
                        print(f"  Prompt ID: {prompt_id}")
                        print(f"  Status: {response.status}")
                        
                        # Print a portion of the workflow to verify it contains correct parameters
                        workflow_json = workflow["prompt"]
                        load_image_nodes = [(node_id, node_data) for node_id, node_data in workflow_json.items()
                                            if node_data.get("class_type") == "LoadImage"]
                        if load_image_nodes:
                            node_id, node_data = load_image_nodes[0]
                            print(f"  LoadImage node {node_id}: {node_data['inputs']['image']}")
                            
                        return True
                    else:
                        print(f"x No prompt_id in response: {data}")
                        return False
                else:
                    error_text = await response.text()
                    print(f"x Failed to send workflow: {response.status} - {error_text}")
                    return False
    except Exception as e:
        print(f"x Error sending workflow to ComfyUI: {str(e)}")
        return False


async def test_manual_post():
    """Test manual POST request with a basic workflow"""
    print("\nTesting manual POST request to ComfyUI API...")
    
    # Create a minimal workflow JSON for testing
    # Using the structure from the Qwen_edit_2511.json file
    workflow_json = {
        "3": {
            "inputs": {
                "image": "nonexistent_image_for_test.jpg"  # This is just for testing the API call
            },
            "class_type": "LoadImage",
            "_meta": {
                "title": "Load Image"
            }
        },
        "6": {
            "inputs": {
                "text": "test prompt",
                "clip": ["3", 0]
            },
            "class_type": "CLIPTextEncode",
            "_meta": {
                "title": "CLIP Text Encode (Prompt)"
            }
        },
        "9": {
            "inputs": {
                "filename_prefix": "test_output",
                "images": ["3", 0]  # Just saving the loaded image for this test
            },
            "class_type": "SaveImage",
            "_meta": {
                "title": "Save Image"
            }
        }
    }
    
    # The ComfyUI API expects the workflow to be in a "prompt" field
    payload = {"prompt": workflow_json}
    
    url = f"{settings.COMFYUI_URL}/prompt"
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload) as response:
                print(f"Response status: {response.status}")
                if response.status != 200:
                    error_text = await response.text()
                    print(f"Error: {error_text}")
                    print("This is expected if the image file doesn't exist or ComfyUI isn't configured properly")
                else:
                    data = await response.json()
                    print(f"Success: {data}")
                return response.status == 200
    except Exception as e:
        print(f"x Error in manual POST: {str(e)}")
        return False


async def run_tests():
    # Test 1: Send actual workflow
    success1 = await test_send_prompt()
    
    # Test 2: Manual POST
    success2 = await test_manual_post()
    
    print(f"\nTest Results:")
    print(f"- Workflow test: {'PASS' if success1 else 'FAIL'}")
    print(f"- Manual POST test: {'PASS' if success2 else 'FAIL'}")
    
    if success1 or success2:
        print("\nV At least one test passed - ComfyUI API appears to be accessible")
    else:
        print("\nx Both tests failed - check ComfyUI configuration")


async def main():
    print("Running ComfyUI API tests...\n")
    
    # Run async tests
    await run_tests()


if __name__ == "__main__":
    asyncio.run(main())


if __name__ == "__main__":
    asyncio.run(main())