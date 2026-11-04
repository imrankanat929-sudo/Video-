@echo off
chcp 65001 >nul
title NOXARGENT_STUDIO - установка
echo === NOXARGENT_STUDIO: подготовка компьютера ===
echo.

rem --- Путь к Рабочему столу (учитывает OneDrive и русскую Windows)
for /f "usebackq delims=" %%D in (`powershell -NoProfile -Command "[Environment]::GetFolderPath('Desktop')"`) do set "NOX_DESKTOP=%%D"
set "STUDIO=%NOX_DESKTOP%\NOXARGENT_STUDIO"
mkdir "%STUDIO%\scripts" 2>nul
set "PATH=%PATH%;%LOCALAPPDATA%\Microsoft\WinGet\Links;%LOCALAPPDATA%\Programs\Python\Python312;%LOCALAPPDATA%\Programs\Python\Python312\Scripts"

rem --- 1. Python 3.9+
set "PY="
py -3 -c "import sys; sys.exit(0 if sys.version_info>=(3,9) else 1)" >nul 2>&1 && set "PY=py -3"
if not defined PY python -c "import sys; sys.exit(0 if sys.version_info>=(3,9) else 1)" >nul 2>&1 && set "PY=python"
if not defined PY (
  echo [..] Устанавливаю Python 3.12...
  winget install -e --id Python.Python.3.12 --scope user --accept-package-agreements --accept-source-agreements
  set "PY=%LOCALAPPDATA%\Programs\Python\Python312\python.exe"
)
%PY% --version || (echo [!!] Python не установился. & pause & exit /b 1)

rem --- 1. FFmpeg
where ffmpeg >nul 2>&1 || (
  echo [..] Устанавливаю FFmpeg...
  winget install -e --id Gyan.FFmpeg --accept-package-agreements --accept-source-agreements
)
where ffmpeg >nul 2>&1 || (echo [!!] FFmpeg не найден. Перезапустите этот файл. & pause & exit /b 1)
echo [OK] FFmpeg найден

rem --- 2. Библиотеки
echo [..] Устанавливаю библиотеки...
%PY% -m pip install --upgrade pip >nul
%PY% -m pip install pillow numpy opencv-python faster-whisper || (echo [!!] Ошибка pip & pause & exit /b 1)

rem --- 3-4. Рабочая папка и тестовый рендер
copy /y "%~dp0render_test.py" "%STUDIO%\scripts\" >nul
echo [..] Рендерю тестовую сцену (1-3 минуты)...
%PY% "%STUDIO%\scripts\render_test.py"
echo.
echo === Готово. test.mp4 лежит на Рабочем столе. ===
pause
