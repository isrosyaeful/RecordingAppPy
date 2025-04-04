import cv2
import numpy as np
import os
import threading
import time
import subprocess
import pyaudio
import wave
from pynput import mouse, keyboard
from mss import mss
from collections import deque
from datetime import datetime

class ScreenRecorder:
    def __init__(self):
        # Initialize MSS and get all monitors
        with mss() as sct:
            self.all_monitors = sct.monitors
            self.monitor_index = 1
            self.resolution = (self.all_monitors[self.monitor_index]['width'],
                             self.all_monitors[self.monitor_index]['height'])
        
        # Video settings (optimized for compression)
        self.fps = 12
        self.fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # Temporary codec
        self.bitrate = "1500k"
        self.encoding_quality = 75
        
        # Audio settings
        self.audio_enabled = True
        self.audio_frames = []
        self.chunk = 1024
        self.format = pyaudio.paInt16
        self.channels = 2
        self.rate = 44100
        
        # Input tracking
        self.running = False
        self.stop_event = threading.Event()
        self.mouse_position = (0, 0)
        self.mouse_clicks = []
        self.click_duration = 0.5
        self.key_presses = deque(maxlen=5)
        self.key_display_duration = 2.0
        
        # Results directory
        self.results_dir = "results"
        os.makedirs(self.results_dir, exist_ok=True)
        
        # Thread management
        self.local = threading.local()
        self.mouse_listener = None
        self.keyboard_listener = None
        self.audio_stream = None
        self.audio_interface = None
        self.temp_files = []

    def start_audio_recording(self):
        if not self.audio_enabled:
            return
            
        self.audio_interface = pyaudio.PyAudio()
        self.audio_frames = []
        
        self.audio_stream = self.audio_interface.open(
            format=self.format,
            channels=self.channels,
            rate=self.rate,
            input=True,
            frames_per_buffer=self.chunk,
            stream_callback=self.audio_callback
        )

    def audio_callback(self, in_data, frame_count, time_info, status):
        self.audio_frames.append(in_data)
        return (in_data, pyaudio.paContinue)

    def combine_audio_video(self, video_path, audio_path, output_path):
        """Combine video and audio using FFmpeg"""
        try:
            cmd = [
                'ffmpeg',
                '-y',  # Overwrite without asking
                '-i', video_path,
                '-i', audio_path,
                '-c:v', 'libx264',
                '-b:v', self.bitrate,
                '-preset', 'fast',
                '-c:a', 'aac',
                '-strict', 'experimental',
                output_path
            ]
            subprocess.run(cmd, check=True, capture_output=True)
            print(f"Combined audio/video saved to {output_path}")
            return True
        except subprocess.CalledProcessError as e:
            print(f"Error combining files: {e.stderr.decode()}")
            return False

    def start(self, monitor_num=1):
        # Reset state
        self.stop_event = threading.Event()
        self.mouse_position = (0, 0)
        self.mouse_clicks = []
        self.key_presses.clear()
        
        # Set monitor
        self.monitor_index = monitor_num
        with mss() as sct:
            monitor = sct.monitors[self.monitor_index]
            self.resolution = (int(monitor['width'] * 0.75), 
                              int(monitor['height'] * 0.75))
        
        # Prepare output paths
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.temp_video = os.path.join(self.results_dir, f"temp_video_{timestamp}.mp4")
        self.temp_audio = os.path.join(self.results_dir, f"temp_audio_{timestamp}.wav")
        self.final_output = os.path.join(self.results_dir, f"output_{timestamp}.mp4")
        
        # Initialize VideoWriter
        self.writer = cv2.VideoWriter(
            self.temp_video,
            self.fourcc,
            self.fps,
            self.resolution,
            isColor=True
        )
        
        if not self.writer.isOpened():
            print(f"Error: Could not open video writer for {self.temp_video}")
            return False
        
        # Start input listeners
        self.start_mouse_listener()
        self.start_keyboard_listener()
        self.start_audio_recording()
        self.running = True
        
        def record():
            try:
                sct = self.get_mss_instance()
                monitor = self.all_monitors[self.monitor_index]
                
                frame_time = 1.0 / self.fps
                while not self.stop_event.is_set():
                    start_time = time.time()
                    
                    # Capture screen
                    img = sct.grab(monitor)
                    frame = np.array(img)
                    frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)
                    frame = cv2.resize(frame, self.resolution)
                    
                    # Add visual overlays
                    self.draw_mouse(frame)
                    self.draw_hotkeys(frame)
                    
                    # Write frame
                    self.writer.write(frame)
                    
                    # Maintain FPS
                    elapsed = time.time() - start_time
                    time.sleep(max(0, frame_time - elapsed))
                    
            except Exception as e:
                print(f"Recording error: {str(e)}")
            finally:
                # Release video resources
                if hasattr(self, 'writer'):
                    self.writer.release()
                
                # Release audio resources
                if self.audio_stream:
                    self.audio_stream.stop_stream()
                    self.audio_stream.close()
                    self.audio_interface.terminate()
                    
                    # Save audio to WAV file
                    with wave.open(self.temp_audio, 'wb') as wf:
                        wf.setnchannels(self.channels)
                        wf.setsampwidth(self.audio_interface.get_sample_size(self.format))
                        wf.setframerate(self.rate)
                        wf.writeframes(b''.join(self.audio_frames))
                
                # Combine audio and video
                if os.path.exists(self.temp_audio) and os.path.exists(self.temp_video):
                    if self.combine_audio_video(self.temp_video, self.temp_audio, self.final_output):
                        # Clean up temp files
                        os.remove(self.temp_video)
                        os.remove(self.temp_audio)
                
                # Stop input listeners
                if self.mouse_listener:
                    self.mouse_listener.stop()
                if self.keyboard_listener:
                    self.keyboard_listener.stop()
                
                print(f"Final output saved to {self.final_output}")
            
        # Start recording thread
        self.recording_thread = threading.Thread(target=record, daemon=True)
        self.recording_thread.start()
        print(f"Recording started with audio @ {self.fps}FPS")
        return True

    # ... (keep existing draw_mouse(), draw_hotkeys(), stop(), and run_recorder() methods) ...
    
    def get_mss_instance(self):
        if not hasattr(self.local, "sct"):
            self.local.sct = mss()
        return self.local.sct

    def draw_hotkeys(self, frame):
        current_time = time.time()
        y_offset = 30
        x_offset = 20
        
        # Display "Hotkeys:" label
        cv2.putText(frame, "Hotkeys:", (x_offset, y_offset), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        y_offset += 30
        
        # Display recent key presses
        for key_str, press_time in reversed(self.key_presses):
            if current_time - press_time < self.key_display_duration:
                alpha = 1.0 - min(1.0, (current_time - press_time) / self.key_display_duration)
                color = (255, int(255 * alpha), int(255 * alpha))  # Fading yellow
                
                cv2.putText(frame, f"> {key_str}", (x_offset, y_offset), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
                y_offset += 30

    def start_keyboard_listener(self):
        def on_press(key):
            try:
                key_str = key.char
            except AttributeError:
                key_str = str(key).replace("Key.", "")  # Handle special keys
            
            self.key_presses.append((key_str, time.time()))

        self.keyboard_listener = keyboard.Listener(on_press=on_press)
        self.keyboard_listener.start()

    def get_next_filename(self, monitor_num=1):
        existing = [f for f in os.listdir(self.results_dir) if f.startswith('output_')]
        nums = [int(f.split('_')[1].split('.')[0]) for f in existing if f.split('_')[1].split('.')[0].isdigit()]
        return f"output_{max(nums) + 1 if nums else 1}.mp4"
    
    def start_mouse_listener(self):
        def on_move(x, y):
            self.mouse_position = (x, y)

        def on_click(x, y, button, pressed):
            if pressed:
                click_time = time.time()
                self.mouse_clicks.append((x, y, button, click_time))
                # Remove old clicks
                self.mouse_clicks = [c for c in self.mouse_clicks 
                                   if time.time() - c[3] < self.click_duration]

        self.mouse_listener = mouse.Listener(
            on_move=on_move,
            on_click=on_click
        )
        self.mouse_listener.start()

        
    def draw_mouse(self, frame):
        # Draw mouse pointer
        x, y = self.mouse_position
        cv2.circle(frame, (x, y), 10, (0, 0, 255), 2)  # Red circle
        
        # Draw recent clicks
        current_time = time.time()
        for click in self.mouse_clicks:
            x, y, button, click_time = click
            if current_time - click_time < self.click_duration:
                color = (0, 255, 0) if button == mouse.Button.left else (255, 0, 0)
                cv2.circle(frame, (x, y), 15, color, 3)
                cv2.putText(frame, "L" if button == mouse.Button.left else "R",
                           (x + 20, y + 5), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
    
    def stop(self):
        if not self.running:
            return
            
        self.stop_event.set()
        self.running = False
        
        if hasattr(self, 'recording_thread'):
            self.recording_thread.join(timeout=2)
        
        print("Recording stopped")

def run_recorder():
    recorder = ScreenRecorder()
    
    # Hotkey configuration
    listener = keyboard.GlobalHotKeys({
        '<ctrl>+<alt>+1': lambda: recorder.start(1),
        '<ctrl>+<alt>+2': lambda: recorder.start(2),
        '<ctrl>+<alt>+q': recorder.stop
    })
    
    listener.start()
    return recorder