"""Test script to verify file processing through worker"""

import asyncio
import os
import shutil
from pathlib import Path
import tempfile

from worker.main import QwenEditWorker
from worker.config import settings


async def test_file_processing():
    """Test that worker processes files from input directory"""
    print("Starting file processing test...")
    
    # Create a temporary image file to simulate user upload
    temp_dir = Path(tempfile.gettempdir())
    test_image = temp_dir / "test_image.jpg"
    
    # Create a dummy image file (we'll copy an existing one if available or create a small dummy file)
    # For this test, we'll assume there's a sample image in the project
    sample_image_path = Path("test/sample_image.jpg")  # This would be a real sample image
    
    # If no sample image exists, create a minimal dummy file for testing purposes
    if not sample_image_path.exists():
        # Create a minimal dummy JPEG file for testing
        with open(test_image, "wb") as f:
            # Minimal JPEG header
            f.write(b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00H\x00H\x00\x00\xff\xdb\x00C\x00')
            f.write(b'\x08\x06\x06\x07\x06\x05\x08\x07\x07\x07\t\t\x08\n\x0c\x14\r\x0c\x0b\x0b\x0c\x19\x12\x13\x0f')
            f.write(b'\xff\xc0\x00\x11\x08\x00\x01\x00\x01\x01\x01\x11\x00\xff\xc4\x0\x14\x10\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x08')
            f.write(b'\xff\xc4\x00\x14\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')
            f.write(b'\xff\xda\x0\x0c\x03\x01\x00\x02\x10\x03\x10\x00\x00\x01\x95\x00\x07\xff\xd9')
    else:
        # Copy sample image to temp location
        shutil.copy(sample_image_path, test_image)
    
    print(f"Created test image: {test_image}")
    
    # Create an instance of the worker
    worker = QwenEditWorker()
    
    # Initialize the worker
    await worker.initialize()
    
    # Manually trigger file processing using the handle_new_file method
    print(f"Triggering processing for file: {test_image}")
    await worker.handle_new_file(str(test_image))
    
    print("File processing triggered. Check logs to verify the job was queued.")
    
    # Cleanup
    if test_image.exists():
        test_image.unlink()
        print(f"Cleaned up test image: {test_image}")


if __name__ == "__main__":
    asyncio.run(test_file_processing())