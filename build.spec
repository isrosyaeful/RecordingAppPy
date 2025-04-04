# build.spec
block_cipher = None

a = Analysis(
    ['main_controller.py'],
    pathex=['D:\\RnD\\Python\\ScreenHotkeysRecorderPy'],  # Add your project path
    binaries=[
        ('C:\\Users\\Gatulz\\miniconda3\\envs\\rox_automation\\python38.dll', '.'),
        ('C:\\Users\\Gatulz\\miniconda3\\envs\\rox_automation\\DLLs\\*.dll', 'DLLs'),
        
        ('C:/Users/Gatulz/miniconda3/envs/rox_automation/Library/bin/openh264-*.dll', '.'),
        ('C:/Users/Gatulz/miniconda3/envs/rox_automation/Library/bin/ffmpeg.exe', '.'),
    ],
    datas=[],
    hiddenimports=[
        'pynput.keyboard._win32',
        'pynput.mouse._win32',
        'cv2',
        'numpy'
    ],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False
)

# Explicitly include Python DLL
py = a.pure[-1]  # Get the python executable
a.binaries.append(('python38.dll', py[1], 'BINARY'))

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    name='recording1',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,  # Keep console for debugging
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None
)