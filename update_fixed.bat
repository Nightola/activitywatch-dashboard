@echo off
echo =================================
echo ActivityWatch Update - Fixed Paths
echo =================================

REM 定义完整路径
set DESKTOP_PATH=C:\Users\Administrator\Desktop
set PYTHON_SCRIPT=%DESKTOP_PATH%\get_activitywatch_data.py
set JSON_FILE=%DESKTOP_PATH%\activitywatch_data.json

echo Desktop: %DESKTOP_PATH%
echo Python: %PYTHON_SCRIPT%
echo JSON: %JSON_FILE%

REM 检查文件
if not exist "%PYTHON_SCRIPT%" (
    echo ERROR: Python script not found at %PYTHON_SCRIPT%
    pause
    exit /b 1
)

REM 切换到桌面
cd /d "%DESKTOP_PATH%"
echo Current directory: %CD%

REM 运行Python脚本
echo Running Python script...
python "%PYTHON_SCRIPT%"
if %errorlevel% neq 0 (
    echo ERROR: Python script failed
    pause
    exit /b 1
)

REM 检查JSON文件
if not exist "%JSON_FILE%" (
    echo ERROR: JSON file not created!
    echo Expected location: %JSON_FILE%
    pause
    exit /b 1
)

echo SUCCESS: Files are in correct locations

REM 继续Git操作
git config user.name "Nightola"
git config user.email "925857461@qq.com"

git add "%JSON_FILE%"
git commit -m "Auto update: %date% %time%"
if %errorlevel% neq 0 (
    echo INFO: No changes to commit
    exit /b 0
)

git push origin main
if %errorlevel% neq 0 (
    git push origin master
    if %errorlevel% neq 0 (
        echo ERROR: GitHub push failed
        pause
        exit /b 1
    )
)

echo =================================
echo SUCCESS: All operations completed
echo =================================