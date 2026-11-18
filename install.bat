@echo off
rem ============================================================
rem  video-clip-cut skill 一键安装（Windows）
rem  双击运行即可把本技能安装到 WorkBuddy 用户技能目录：
rem  %USERPROFILE%\.workbuddy\skills\video-clip-cut
rem  安装后重启 WorkBuddy 会话即可通过 "剪切片/精剪" 等指令触发。
rem ============================================================
setlocal
set DEST=%USERPROFILE%\.workbuddy\skills\video-clip-cut
set SRC=%~dp0

echo Installing video-clip-cut skill ...
echo   From: %SRC%
echo   To  : %DEST%
echo.

if not exist "%USERPROFILE%\.workbuddy\skills" mkdir "%USERPROFILE%\.workbuddy\skills"

xcopy /E /I /Y "%SRC%" "%DEST%\" >nul
if errorlevel 1 (
  echo [ERROR] Install failed.
  pause
  exit /b 1
)

echo [OK] Installed. Files:
dir /b "%DEST%"
echo.
echo Restart WorkBuddy session to load the skill.
pause
