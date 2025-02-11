#!/bin/bash

# Realtime Whisper Translation App setup script

echo "Realtime Whisper Translation App"

# Pre-checks
if [ ! -f "transcribe_audio.py" ]; then
    echo "Error: 'transcribe_audio.py' not found. Make sure you run the setup script in the same directory as the source code."
    exit 1
fi

echo "Checking for Python 3.10.x"
echo "Running command: python -V"
python_version=$(python -V 2>&1)
echo "$python_version"

# User verification for Python version
echo -n "Does this show Python 3.10.x? (Y/N): "
read user_check

if [[ ! "$user_check" =~ ^[Yy]$ ]]; then
    echo "It seems you do not have Python 3.10.x installed."
    echo "Please download and install Python 3.10.10 from the following link:"
    echo "https://www.python.org/downloads/release/python-31010/"
    echo -n "If you have Python 3.10.x installed but it's not in your PATH, enter the full path to the python binary (e.g., /path/to/python): "
    read python_path
    if [ -z "$python_path" ]; then
        echo "Python 3.10.x is required. Exiting..."
        exit 1
    fi
    python="$python_path"
else
    python="python"
fi

# Pause for user acknowledgment
read -p "Press Enter to continue..."

# Prepare environment
clear
if [ -d "data_whisper" ]; then
    echo -n "Python environment 'data_whisper' already exists. Reinstall it? [y/n]: "
    read reinstall
    if [ "$reinstall" == "y" ] || [ "$reinstall" == "Y" ]; then
        echo "Deleting existing environment..."
        deactivate 2>/dev/null
        rm -rf data_whisper
    else
        echo "Operation cancelled by user."
        exit 0
    fi
fi

echo "Creating a new Python virtual environment..."
$python -m venv data_whisper

echo "Activating the environment..."
source data_whisper/bin/activate

# Install dependencies
echo "Upgrading pip to the latest version..."
python -m pip install --upgrade pip

echo "Installing wheel and setuptools-rust..."
pip install wheel
pip install setuptools-rust

if [ ! -f "requirements.txt" ]; then
    echo "'requirements.txt' not found. Please ensure it is in the current directory."
    deactivate
    exit 1
fi

echo "Installing requirements from 'requirements.txt'..."
pip install -r requirements.txt

# CUDA patch
echo "Applying CUDA patch to install GPU versions of PyTorch packages..."
pip uninstall --yes torch torchvision torchaudio
pip cache purge
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu124

echo "Whisper translation environment setup completed!"

# Creating a shortcut script
echo "Creating a shortcut script for the translation app..."
cat > livetranslation.sh << 'EOL'
#!/bin/bash
source "$(dirname "$0")/data_whisper/bin/activate"
# Include ffmpeg path if available
if [ -f "ffmpeg_path.sh" ]; then
    source ffmpeg_path.sh
fi
python "$(dirname "$0")/transcribe_audio.py" --ram 4gb --non_english --translate
read -p "Press enter to exit..."
EOL

chmod +x livetranslation.sh

echo "Shortcut 'livetranslation.sh' created in the current directory."
echo "You can edit this file with any text editor if necessary."
read -p "Press Enter to continue..."

echo "Setting up Environment Stuff..."
$python set_up_env.py

echo "Setup completed successfully!"
