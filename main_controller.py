from screen_recorder import run_recorder
from input_logger import run_logger
import threading
import time
import sys

def main():
    print("Recording System v2.0")
    print("Hotkeys: Ctrl+Alt+1 to start recording screen 1, Ctrl+Alt+2 to start recording screen 2, Ctrl+Alt+Q to stop")
    print("Press Ctrl+C to exit\n")
    
    recorder = run_recorder()
    logger = run_logger()
    
    try:
        while True:
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("\nShutting down...")
        recorder.stop()
        logger.stop()
        time.sleep(1)  # Allow time for cleanup
        sys.exit(0)

if __name__ == "__main__":
    main()