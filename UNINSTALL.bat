@echo off
setlocal EnableExtensions EnableDelayedExpansion
title MemoryMonitorNMI - Uninstall

set "APP_NAME=MemoryMonitorNMI"
set "USER_START=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\%APP_NAME%.lnk"
set "ALL_START=%ProgramData%\Microsoft\Windows\Start Menu\Programs\StartUp\%APP_NAME%.lnk"

echo ========= %APP_NAME% Uninstall =========

taskkill /IM "%APP_NAME%.exe" /F >nul 2>&1

for %%T in ("%APP_NAME%" "%APP_NAME% (User)" "%APP_NAME% (All Users)") do (
  schtasks /Delete /TN "%%~T" /F >nul 2>&1
)

if exist "%USER_START%" del /F /Q "%USER_START%" >nul 2>&1
if exist "%ALL_START%"  del /F /Q "%ALL_START%"  >nul 2>&1

reg delete "HKCU\Software\Microsoft\Windows\CurrentVersion\Run" /v "%APP_NAME%" /f >nul 2>&1
reg delete "HKCU\Software\Microsoft\Windows\CurrentVersion\RunOnce" /v "%APP_NAME%" /f >nul 2>&1
reg delete "HKLM\Software\Microsoft\Windows\CurrentVersion\Run" /v "%APP_NAME%" /f >nul 2>&1
reg delete "HKLM\Software\Microsoft\Windows\CurrentVersion\RunOnce" /v "%APP_NAME%" /f >nul 2>&1

rmdir /S /Q "%LOCALAPPDATA%\%APP_NAME%" >nul 2>&1
rmdir /S /Q "%APPDATA%\%APP_NAME%" >nul 2>&1
rmdir /S /Q "C:\ProgramData\%APP_NAME%" >nul 2>&1

echo.
echo Uninstall complete.
pause
endlocal
