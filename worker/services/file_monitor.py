import asyncio
import os
from pathlib import Path
from typing import Callable
import logging
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

logger = logging.getLogger(__name__)

class InputFileHandler(FileSystemEventHandler):
    """Handle new files in the input directory"""
    
    def __init__(self, callback: Callable[[str], None]):  # Can be sync or async function
        super().__init__()
        self.callback = callback
    
    def on_created(self, event):
        if not event.is_directory:
            # Check if it's an image file
            ext = Path(event.src_path).suffix.lower()
            if ext in ['.png', '.jpg', '.jpeg']:
                logger.info(f"New image file detected: {event.src_path}")
                
                # Handle the callback appropriately
                if asyncio.iscoroutinefunction(self.callback):
                    # If callback is a coroutine, we need to schedule it properly
                    # This is tricky when called from a non-async thread
                    try:
                        loop = asyncio.get_running_loop()
                        if loop:
                            asyncio.run_coroutine_threadsafe(self.callback(event.src_path), loop)
                    except RuntimeError:
                        # No running event loop in this thread
                        logger.error("No running event loop in this thread - cannot schedule coroutine")
                else:
                    # If it's a regular function, just call it directly
                    self.callback(event.src_path)


class FileMonitor:
    """Monitor input directory for new files and trigger processing"""
    
    def __init__(self, input_dir: str, callback: Callable[[str], None]):
        self.input_dir = Path(input_dir)
        self.callback = callback
        self.observer = Observer()
        self.handler = InputFileHandler(callback)
        
    def start(self):
        """Start monitoring the directory"""
        self.observer.schedule(self.handler, str(self.input_dir), recursive=False)
        self.observer.start()
        logger.info(f"Started monitoring directory: {self.input_dir}")
    
    def stop(self):
        """Stop monitoring the directory"""
        self.observer.stop()
        self.observer.join()
        logger.info(f"Stopped monitoring directory: {self.input_dir}")
    
    async def run(self):
        """Run the monitor indefinitely"""
        self.start()
        try:
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            logger.info("File monitor interrupted by user")
        finally:
            self.stop()