@echo off
setlocal enabledelayedexpansion
Title Realtime Whisper Translation App Setup

:prechecks

if NOT exist transcribe_audio.py goto EoF_Error

Echo Checking for Python 3.10.x
echo Running command: python -V
python -V
echo.

rem Prompt user to verify the Python version
set /p user_check="Does this show Python 3.10.x? (Y/N): "
if /i "%user_check%" neq "Y" (
    echo It seems you do not have Python 3.10.x installed.
    echo Please download and install Python 3.10.10 from the following link:
    echo https://www.python.org/downloads/release/python-31010/
    echo.
    set /p filepath="If you have Python 3.10.x installed but not in PATH, enter the path to the file python.exe for 3.10.x (e.g., C:\path\to\python\python.exe): "

    echo Using this for python: !filepath!
    set "python=!filepath!"
) else (
    rem Set default python if user confirms Python 3.10.x is installed
    set "python=python"
)

pause

goto :prepare_environment

:prepare_environment
cls
if exist "data_whisper" (
    set /p reinstall="Python environment 'data_whisper' already exists. Reinstall it? [Y/N]: "
    if /i "!reinstall!"=="Y" (
        echo Deleting existing environment...
        rmdir /s /q data_whisper
    ) else (
        echo Operation cancelled by user.
        pause
        exit /b
    )
)

echo Creating a new Python virtual environment...
!python! -m venv data_whisper

echo Activating the environment...
call data_whisper\Scripts\activate.bat

:install_dependencies
echo Upgrading pip to the latest version...
python.exe -m pip install --upgrade pip

echo Installing wheel and setuptools-rust...
pip install wheel
pip install setuptools-rust

echo Checking for 'requirements.txt'...
if not exist "requirements.txt" (
    echo 'requirements.txt' not found. Please ensure it is in the current directory.
    exit /b
)

echo Installing requirements from 'requirements.txt'...
pip install -r requirements.txt

:cuda_patch
echo Applying CUDA patch to install GPU versions of PyTorch packages...
pip uninstall --yes torch torchvision torchaudio

pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu124

echo Whisper translation environment setup completed!

:create_shortcut
echo Creating a shortcut batch file for the translation app...
(
    echo @echo off
    echo cls
    echo call "data_whisper\Scripts\activate.bat"
    echo call ffmpeg_path.bat
    echo python "transcribe_audio.py" --ram 4gb --non_english --translate
    echo pause
) > "livetranslation.bat"

echo Shortcut 'livetranslation.bat' created in the current directory.
echo You can edit this file with notepad if necessary.
pause

Echo Setting up Environment Stuff.
!python! set_up_env.py

exit /b

:EoF_Error
Echo can not fnd transcribe_audio.py
Echo Did you run as admin? If so DO NOT run as admin!
Echo. Please make sure you run setup in the same location as the source code.
Echo. If you are using powershell, Do not. Use command prompt instead.
pause
exit /b
