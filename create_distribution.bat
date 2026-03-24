@echo off
echo Bob AI Distribution Package Creator
echo ====================================
echo.

REM Create distribution folder
if not exist "BobAI_Distribution" mkdir "BobAI_Distribution"

REM Copy all necessary files
echo Copying files...
copy "*.py" "BobAI_Distribution\"
copy "requirements.txt" "BobAI_Distribution\"
xcopy "src" "BobAI_Distribution\src\" /E /I /Y
xcopy "data" "BobAI_Distribution\data\" /E /I /Y
xcopy "config" "BobAI_Distribution\config\" /E /I /Y
if exist "models" xcopy "models" "BobAI_Distribution\models\" /E /I /Y

REM Create user instructions
echo Creating user instructions...
(
echo # Bob AI - Easy Setup
echo.
echo ## Quick Start:
echo 1. Install Python 3.8+ from python.org
echo 2. Open command prompt in this folder
echo 3. Run: pip install -r requirements.txt
echo 4. Run: python main.py
echo 5. Say "Hey Bob" to start talking!
echo.
echo ## What you get:
echo - Offline voice assistant
echo - Wake word detection
echo - Learning conversations
echo - Natural voice responses
echo.
echo ## Troubleshooting:
echo - Make sure microphone is connected
echo - Allow microphone permissions
echo - First run may take time to download models
echo.
echo Enjoy Bob AI!
) > "BobAI_Distribution\README.txt"

REM Create simple run script
(
echo @echo off
echo echo Starting Bob AI...
echo python main.py
echo pause
) > "BobAI_Distribution\run_bob.bat"

echo.
echo ✅ Distribution package created: BobAI_Distribution\
echo 📦 Ready to share! Users just need Python installed.
echo.
pause