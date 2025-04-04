# Input Logger & Screen Recorder

A Python-based application that logs user input (keyboard & mouse) and records the screen.

## Features
✅ Records screen activity 
✅ Logs keyboard and mouse input (shows in the recording as well) 
✅ Saves logs in CSV format  
✅ Multi-threaded for efficiency 
✅ Simple start/stop hotkeys  to record screen 1 or screen 2

## Installation

### Prerequisites
- Python 3.8+
- Pip package manager

### Install Dependencies
```sh
pip install -r requirements.txt
```

## Usage

### Run the application (to test the application)
```sh
python main.py
```

### To build the into executable application 
```sh
pyinstaller --clean build.spec
```

### Keyboard Hotkeys to start/stop recording
- **Ctrl + Alt + 1** → Start recording and logging screen 1
- **Ctrl + Alt + 2** → Start recording and logging screen 2
- **Ctrl + Alt + Q** → Stop recording and logging screen  

## File Output

find the recording and hotkeys log files in the folder results

## Project Structure (main code)
```
📂 my_project  
 ┣ 📂 dist/ 
 ┣ 📂 results/  
 ┣ 📜 input_logger.py  
 ┣ 📜 screen_recorder.py  
 ┣ 📜 main_controller.py  
 ┣ 📜 build.spec  
 ┣ 📜 requirements.txt  
 ┣ 📜 README.md  
```

## License
This project is licensed under the  GPL-3.0 license.

## Author
👤 **Your Name**  
- GitHub: [@isrosyaeful](https://github.com/isrosyaeful)  
- LinkedIn: [Isro Syaeful Iman](https://linkedin.com/in/isrosyaeful)  

## Contributing
Pull requests are welcome! Open an issue if you find a bug or have a feature request.

