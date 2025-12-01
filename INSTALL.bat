@echo off
setlocal EnableExtensions EnableDelayedExpansion
title MemoryMonitorNMI - Install (Startup Shortcut + Self-Repair)

set "APP_NAME=MemoryMonitorNMI"
set "EXE=%~dp0MemoryMonitorNMI.exe"
set "TASK=%APP_NAME%"
set "USER_START=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\%APP_NAME%.lnk"
set "ALL_START=%ProgramData%\Microsoft\Windows\Start Menu\Programs\StartUp\%APP_NAME%.lnk"

echo ========= %APP_NAME% Install (Startup Shortcut + Repairs) =========

:: 0) Basic check
if not exist "%EXE%" (
  echo ERROR: "%EXE%" not found. Place this INSTALL.bat next to %APP_NAME%.exe
  pause & exit /b 1
)

:: 1) Stop any running instance
echo Stopping running process (if any)...
taskkill /IM "%APP_NAME%.exe" /F >nul 2>&1

:: 2) Self-Repair Startup Shortcut
echo Checking for old or invalid startup shortcuts...

if exist "%USER_START%" (
    powershell -NoProfile -ExecutionPolicy Bypass -Command ^
      "$lnk='%USER_START%';" ^
      "$w=New-Object -ComObject WScript.Shell;" ^
      "$s=$w.CreateShortcut($lnk);" ^
      "if($s.TargetPath -ne '%EXE%'){ Remove-Item '%USER_START%' -Force }"
)

if exist "%ALL_START%" (
    powershell -NoProfile -ExecutionPolicy Bypass -Command ^
      "$lnk='%ALL_START%';" ^
      "$w=New-Object -ComObject WScript.Shell;" ^
      "$s=$w.CreateShortcut($lnk);" ^
      "if($s.TargetPath -ne '%EXE%'){ Remove-Item '%ALL_START%' -Force }"
)

:: 3) Clean previous auto-start hooks
echo Cleaning auto-start hooks...
schtasks /Delete /TN "%TASK%" /F >nul 2>&1
schtasks /Delete /TN "%TASK% (User)" /F >nul 2>&1
schtasks /Delete /TN "%TASK% (All Users)" /F >nul 2>&1
reg delete "HKCU\Software\Microsoft\Windows\CurrentVersion\Run" /v "%APP_NAME%" /f >nul 2>&1
reg delete "HKLM\Software\Microsoft\Windows\CurrentVersion\Run" /v "%APP_NAME%" /f >nul 2>&1
if exist "%USER_START%" del /F /Q "%USER_START%" >nul 2>&1
if exist "%ALL_START%"  del /F /Q "%ALL_START%"  >nul 2>&1

:: 4) Prepare folder (same behavior as FolderMonitorAdrian)
echo Preparing local app data folder...
mkdir "%LOCALAPPDATA%\%APP_NAME%" >nul 2>&1

:: 5) Fix config.json formatting
if exist "%~dp0config.json" (
  echo Checking config.json formatting...
  powershell -NoProfile -ExecutionPolicy Bypass -Command ^
    "$p='%~dp0config.json';" ^
    "$j=Get-Content $p -Raw;" ^
    "$j=$j -replace '\\\\','/';" ^
    "$j=$j -replace '/+','/';" ^
    "[IO.File]::WriteAllText($p,$j,[Text.UTF8Encoding]::new($false));"
)

:: 6) Create Startup shortcut (correct folder & working dir)
echo Creating Startup shortcut...
powershell -NoProfile -ExecutionPolicy Bypass -Command ^
  "$WScript = New-Object -ComObject WScript.Shell;" ^
  "$lnk = $WScript.CreateShortcut('%USER_START%');" ^
  "$lnk.TargetPath = '%EXE%';" ^
  "$lnk.WorkingDirectory = '%~dp0';" ^
  "$lnk.IconLocation = '%EXE%,0';" ^
  "$lnk.Save();"

:: 7) Delay (Option 1) — improves tray reliability
echo Adding startup delay for safe tray loading...
timeout /t 3 >nul

:: 8) Launch now for confirmation
echo Starting %APP_NAME% now...
start "" "%EXE%"

echo.
echo Install complete. MemoryMonitorNMI will auto-start on login.
pause
endlocal
