import cv2
import csv
import numpy as np
from moviepy.editor import VideoFileClip

class RecordingMerger:
    def __init__(self, video_file='results/output_7.mp4', log_file='results/input_log_7.csv'):
        self.video = VideoFileClip(video_file)
        self.logs = []
        with open(log_file, 'r') as f:
            reader = csv.reader(f)
            next(reader)  # Skip header
            self.logs = list(reader)
        self.current_frame = 0  # Track frame count manually

    def add_input_overlay(self, output_file='results/merged_output_7.mp4'):
        def process_frame(frame):
            # Convert frame to OpenCV format
            frame_cv = cv2.cvtColor(np.array(frame), cv2.COLOR_RGB2BGR)
            
            # Calculate current timestamp (manual method)
            t = self.current_frame / self.video.fps
            
            # print(self)
            # print(self.current_frame)
            # print(self.video.fps)
            self.current_frame += 1
            
            # Find relevant events within ±0.1 seconds
            relevant_events = [
                log for log in self.logs 
                if abs(float(log[0]) - t) < 0.1
            ]
            
            # Add overlay
            y_offset = 50
            for event in relevant_events:
                text = f"{event[1]}: {event[2]}"
                cv2.putText(frame_cv, text, (10, y_offset), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,255,255), 2)
                y_offset += 30
                
                # Draw mouse position
                if 'mouse' in event[1] and '(' in event[2]:
                    coords = event[2].split('(')[-1].split(')')[0].split(',')
                    try:
                        x, y = int(coords[0]), int(coords[1])
                        cv2.circle(frame_cv, (x,y), 10, (0,0,255), 2)
                    except (ValueError, IndexError):
                        pass
            
            return cv2.cvtColor(frame_cv, cv2.COLOR_BGR2RGB)

        # Apply processing and save
        processed_clip = self.video.fl_image(process_frame)
        processed_clip.write_videofile(
            output_file, 
            codec='libx264', 
            audio=False,
            threads=4,  # Helps with performance
            ffmpeg_params=['-crf', '18']  # Better quality
        )

if __name__ == "__main__":
    merger = RecordingMerger()
    merger.add_input_overlay()