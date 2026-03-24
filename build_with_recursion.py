import sys
import subprocess

# Increase recursion limit to maximum
sys.setrecursionlimit(50000)

# Run PyInstaller with all arguments
cmd = [
    sys.executable, '-m', 'PyInstaller',
    '--onefile',
    '--name=BobAI_Portable',
    '--console',
    '--add-data=models;models',
    '--add-data=response;response', 
    '--add-data=src;src',
    '--add-data=config;config',
    '--add-data=voices-v1.0.bin;.',
    '--add-data=kokoro-v1.0.onnx;.',
    '--hidden-import=kokoro_onnx',
    '--hidden-import=sounddevice',
    '--hidden-import=soundfile',
    '--hidden-import=onnxruntime',
    '--hidden-import=sentence_transformers',
    '--hidden-import=faiss',
    '--hidden-import=pyttsx3',
    '--hidden-import=vosk',
    '--hidden-import=pyaudio',
    '--hidden-import=flask',
    '--hidden-import=flask_cors',
    '--hidden-import=win32com.client',
    'main.py'
]

subprocess.run(cmd)