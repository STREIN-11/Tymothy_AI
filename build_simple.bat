@echo off
echo Building Bob AI Portable...
echo.

REM Clean previous builds
if exist "dist" rmdir /s /q "dist"
if exist "build" rmdir /s /q "build"

REM Use python -m pyinstaller with Whisper assets and tkinter included
python -m PyInstaller --onefile --clean --noconfirm --name=BobAI_Portable --console --add-data="models;models" --add-data="response;response" --add-data="src;src" --add-data="config;config" --add-data=".env;." --hidden-import=edge_tts --hidden-import=edge_tts.communicate --hidden-import=edge_tts.tts --hidden-import=edge_tts.utils --hidden-import=edge_tts.exceptions --hidden-import=aiohttp --hidden-import=certifi --hidden-import=sounddevice --hidden-import=soundfile --hidden-import=openai --hidden-import=dotenv --hidden-import=bs4 --hidden-import=requests --collect-all whisper --collect-all torch --collect-all numpy --collect-all tkinter --collect-all sentence_transformers --collect-all faiss main.py

if exist "dist\BobAI_Portable.exe" (
    echo.
    echo ✅ Build successful!
    echo 📁 Executable created: dist\BobAI_Portable.exe
    echo.
    
    REM Create portable folder
    if not exist "BobAI_Portable" mkdir "BobAI_Portable"
    copy "dist\BobAI_Portable.exe" "BobAI_Portable\"
    
    REM Copy data folders if they exist
    if exist "data" xcopy "data" "BobAI_Portable\data\" /E /I /Y
    if exist "models" xcopy "models" "BobAI_Portable\models\" /E /I /Y
    if exist "config" xcopy "config" "BobAI_Portable\config\" /E /I /Y
    if exist "response" xcopy "response" "BobAI_Portable\response\" /E /I /Y
    if exist ".env" copy ".env" "BobAI_Portable\"

    
    REM Create response folder if it doesn't exist
    if not exist "BobAI_Portable\response" mkdir "BobAI_Portable\response"
    
    echo 📦 Portable package created: BobAI_Portable\
    echo.
    echo Ready to distribute!
    echo Just share the BobAI_Portable folder.
) else (
    echo ❌ Build failed!
)

echo.
pause