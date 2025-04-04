import csv
import os
import time
from pynput import keyboard, mouse
from datetime import datetime

class InputLogger:
    def __init__(self):
        self.log = []
        self.start_time = None
        self.running = False
        self.results_dir = "results"
        os.makedirs(self.results_dir, exist_ok=True)
        
    def get_next_filename(self):
        existing = [f for f in os.listdir(self.results_dir) if f.startswith('input_log_')]
        nums = [int(f.split('_')[2].split('.')[0]) for f in existing if f.split('_')[2].split('.')[0].isdigit()]
        return f"input_log_{max(nums) + 1 if nums else 1}.csv"
        
    def start(self):
        
        self.running = True
        self.start_time = time.time()
        self.keyboard_listener = keyboard.Listener(
            on_press=self.on_press,
            on_release=self.on_release
        )
        self.mouse_listener = mouse.Listener(
            on_click=self.on_click,
            on_move=self.on_move
        )
        self.keyboard_listener.start()
        self.mouse_listener.start()
        print("Input logging started")

    def stop(self):
        self.running = False
        output_path = os.path.join(self.results_dir, self.get_next_filename())
        with open(output_path, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Timestamp', 'Event', 'Details'])
            writer.writerows(self.log)
        print(f"Input log saved to {output_path}")
        self.keyboard_listener.stop()
        self.mouse_listener.stop()

    def log_event(self, event_type, details):
        if not self.start_time:
            return
        self.log.append([time.time() - self.start_time, event_type, str(details)])

    def on_press(self, key):
        self.log_event('key_press', key)

    def on_release(self, key):
        self.log_event('key_release', key)

    def on_click(self, x, y, button, pressed):
        self.log_event('mouse_click' if pressed else 'mouse_release', f"{button.name} ({x},{y})")

    def on_move(self, x, y):
        self.log_event('mouse_move', f"({x},{y})")

def run_logger():
    logger = InputLogger()
    listener = keyboard.GlobalHotKeys({
        '<ctrl>+<alt>+s': logger.start,
        '<ctrl>+<alt>+1': logger.start,
        '<ctrl>+<alt>+2': logger.start,
        '<ctrl>+<alt>+q': logger.stop
    })
    listener.start()
    return logger