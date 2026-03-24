import PyInstaller.__main__
import os
import shutil

def build_executable():
    """Build Bob AI as a single executable"""
    
    # Clean previous builds
    if os.path.exists('dist'):
        shutil.rmtree('dist')
    if os.path.exists('build'):
        shutil.rmtree('build')
    
    # PyInstaller arguments
    args = [
        'main.py',
        '--onefile',
        '--name=BobAI',
        '--add-data=data;data',
        '--add-data=config;config',
        '--add-data=models;models',
        '--hidden-import=pyttsx3',
        '--hidden-import=vosk',
        '--hidden-import=pyaudio',
        '--hidden-import=faiss',
        '--hidden-import=sentence_transformers',
        '--hidden-import=torch',
        '--hidden-import=transformers',
        '--hidden-import=numpy',
        '--hidden-import=sklearn',
        '--collect-all=sentence_transformers',
        '--collect-all=transformers',
        '--collect-all=torch',
        '--noconsole',  # Remove this if you want console output
    ]
    
    print("Building Bob AI executable...")
    PyInstaller.__main__.run(args)
    print("Build complete! Check the 'dist' folder for BobAI.exe")

if __name__ == "__main__":
    build_executable()