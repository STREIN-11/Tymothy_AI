@echo off
echo Bob AI Portable Setup
echo =====================
echo.

REM Check if running as administrator
net session >nul 2>&1
if %errorLevel% == 0 (
    echo Running as Administrator - Good!
) else (
    echo Note: Some features may require administrator privileges
)

echo.
echo Setting up Bob AI...

REM Create shortcuts
echo Creating desktop shortcut...
powershell "$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%USERPROFILE%\Desktop\Bob AI.lnk'); $Shortcut.TargetPath = '%~dp0BobAI_Portable.exe'; $Shortcut.WorkingDirectory = '%~dp0'; $Shortcut.Save()"

REM Set microphone permissions (Windows 10/11)
echo Checking microphone permissions...
powershell "if (Get-Command 'Get-AppxPackage' -ErrorAction SilentlyContinue) { Write-Host 'Please allow microphone access when prompted' }"

echo.
echo Setup complete!
echo.
echo You can now:
echo 1. Double-click the desktop shortcut "Bob AI"
echo 2. Or run BobAI_Portable.exe directly
echo.
echo Say "Hey Bob" to start talking!
echo.
pause