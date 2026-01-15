#!/usr/bin/env python3

"""Test script to verify worker imports and structure"""

def test_worker_imports():
    """Test that all worker modules can be imported"""
    try:
        # Test main imports
        from worker.main import QwenEditWorker
        print("✅ Main worker class imported successfully")
        
        # Test config
        from worker.config import settings
        print("✅ Config imported successfully")
        
        # Test GPU lock
        from worker.gpu.lock import GPULock
        print("✅ GPU lock imported successfully")
        
        # Test queue
        from worker.job_queue.job_queue import JobQueue, Job
        print("✅ Job queue imported successfully")
        
        # Test retry strategy
        from worker.retry.strategy import RetryStrategy
        print("✅ Retry strategy imported successfully")
        
        # Test processors
        from worker.processors.image_editor import ImageEditorProcessor
        from worker.processors.result_handler import ResultHandler
        print("✅ Processors imported successfully")
        
        # Test services
        from worker.services.backend_client import BackendAPIClient
        from worker.services.comfyui_client import ComfyUIClient
        from worker.services.telegram_client import TelegramClient
        print("✅ Services imported successfully")
        
        # Test utils
        from worker.utils.logger import setup_logger
        print("✅ Utils imported successfully")
        
        print("\n🎉 All worker imports successful!")
        return True
        
    except Exception as e:
        print(f"❌ Import error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_worker_imports()