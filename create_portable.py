"""
Portable Bob AI Builder
Creates a standalone executable that works on any Windows system
"""

import subprocess
import os
import shutil

def create_portable_bob():
    """Create portable Bob executable"""
    
    print("Creating Portable Bob AI...")
    
    # Clean previous builds
    if os.path.exists('dist'):
        shutil.rmtree('dist')
    if os.path.exists('build'):
        shutil.rmtree('build')
    
    # Simple PyInstaller command for maximum compatibility
    cmd = [
        'pyinstaller',
        '--onefile',
        '--name=BobAI_Portable',
        '--add-data=data;data',
        '--add-data=config;config',
        '--hidden-import=pyttsx3',
        '--hidden-import=vosk',
        '--hidden-import=pyaudio',
        '--hidden-import=faiss',
        '--hidden-import=sentence_transformers',
        '--hidden-import=numpy',
        '--hidden-import=json',
        '--hidden-import=csv',
        '--hidden-import=threading',
        '--console',  # Keep console for user feedback
        '--distpath=portable',
        'main.py'
    ]
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("✅ Build successful!")
        print("📁 Executable created: portable/BobAI_Portable.exe")
        
        # Create portable package
        create_portable_package()
        
    except subprocess.CalledProcessError as e:
        print("❌ Build failed:")
        print(e.stderr)

def create_portable_package():
    """Create complete portable package"""
    
    package_dir = "BobAI_Portable_Package"
    
    # Create package directory
    if os.path.exists(package_dir):
        shutil.rmtree(package_dir)
    os.makedirs(package_dir)
    
    # Copy executable
    shutil.copy("portable/BobAI_Portable.exe", package_dir)
    
    # Copy essential folders
    if os.path.exists("data"):
        shutil.copytree("data", os.path.join(package_dir, "data"))
    if os.path.exists("models"):
        shutil.copytree("models", os.path.join(package_dir, "models"))
    
    # Create README for users
    readme_content = """
# Bob AI - Portable Version

## How to Use:
1. Double-click BobAI_Portable.exe
2. Say "Hey Bob" to wake up the assistant
3. Ask your questions!

## Requirements:
- Windows 10/11
- Microphone access
- No Python installation needed!

## Features:
- Offline voice assistant
- Wake word detection ("Hey Bob")
- Learning from conversations
- Natural voice responses

## Troubleshooting:
- If microphone doesn't work, check Windows permissions
- First startup may take 10-30 seconds to load models
- Antivirus may flag the exe - it's safe to allow

Enjoy using Bob AI!
"""
    
    with open(os.path.join(package_dir, "README.txt"), "w") as f:
        f.write(readme_content)
    
    print(f"📦 Portable package created: {package_dir}/")
    print("🚀 Ready to distribute!")

if __name__ == "__main__":
    create_portable_bob()