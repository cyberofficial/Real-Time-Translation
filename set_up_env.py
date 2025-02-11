"""Environment setup script for Synthalingua.

This script handles the installation and configuration of required tools:
- FFmpeg: A multimedia framework for processing audio and video files
- yt-dlp: A video downloader for YouTube and other sites
- 7zr: A tool for extracting .7z files

The script will create a batch file that sets up the necessary PATH environment
variables for these tools to work with Synthalingua.
"""

import os
import platform
import requests
import subprocess
import sys
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Optional
from tqdm import tqdm

@dataclass
class Config:
    """Configuration settings for the environment setup."""
    FFMPEG_URL: str = 'https://www.gyan.dev/ffmpeg/builds/ffmpeg-git-full.7z'
    YTDLP_URL: str = 'https://github.com/yt-dlp/yt-dlp/releases/download/2025.01.26/yt-dlp_win.zip'
    SEVEN_ZIP_URL: str = 'https://www.7-zip.org/a/7zr.exe'
    
    def __post_init__(self) -> None:
        """Initialize paths based on current working directory."""
        self.FFMPEG_ROOT_PATH: Path = Path.cwd() / 'ffmpeg'
        self.YTDLP_PATH: Path = Path.cwd() / 'yt-dlp_win'
        self.FFMPEG_ARCHIVE: str = 'ffmpeg.7z'
        self.YTDLP_ARCHIVE: str = 'yt-dlp_win.zip'
        self.SEVEN_ZIP_EXEC: str = '7zr.exe'
        self.CONFIG_FILE: str = 'ffmpeg_path.bat'


class DownloadManager:
    """Handles file downloads and extractions."""

    @staticmethod
    def download_file(url: str, filename: str) -> None:
        """Download a file from a URL with progress display.
        
        Args:
            url: The URL to download from
            filename: The name to save the file as
        
        Raises:
            requests.exceptions.RequestException: If download fails
        """
        print(f"Downloading {filename} from {url}...")
        response = requests.get(url, stream=True)
        response.raise_for_status()

        total_size = int(response.headers.get('content-length', 0))
        with open(filename, 'wb') as file, tqdm(
                desc=filename,
                total=total_size,
                unit='iB',
                unit_scale=True,
                unit_divisor=1024,
        ) as bar:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)
                bar.update(len(chunk))

        print(f"{filename} downloaded successfully.")

    @staticmethod
    def extract_7z(file_path: str, extract_to: str, seven_zip_exec: str) -> None:
        """Extract a .7z file using 7zr.exe.
        
        Args:
            file_path: Path to the .7z file
            extract_to: Directory to extract to
            seven_zip_exec: Path to 7zr executable
            
        Raises:
            subprocess.CalledProcessError: If extraction fails
        """
        print(f"Extracting {file_path} with 7zr...")
        subprocess.run([seven_zip_exec, 'x', file_path, f'-o{extract_to}'], check=True)
        print(f"{file_path} extracted successfully.")

    @staticmethod
    def extract_zip(file_path: str, extract_to: str) -> None:
        """Extract a .zip file to a specified directory.
        
        Args:
            file_path: Path to the zip file
            extract_to: Directory to extract to
            
        Raises:
            zipfile.BadZipFile: If zip file is corrupted
        """
        print(f"Extracting {file_path}...")
        with zipfile.ZipFile(file_path, 'r') as zip_ref:
            zip_ref.extractall(extract_to)
        print(f"{file_path} extracted successfully.")


class EnvironmentSetup:
    """Handles the setup of required tools and environment."""

    def __init__(self):
        self.config = Config()
        self.downloader = DownloadManager()

    def find_ffmpeg_bin_path(self, root_path: Path) -> Optional[Path]:
        """Find the bin directory containing ffmpeg.exe.
        
        Args:
            root_path: Root directory to search in
            
        Returns:
            Path to ffmpeg bin directory if found, None otherwise
        """
        print("Finding path for ffmpeg...")
        try:
            for root, _, files in os.walk(root_path):
                if 'ffmpeg.exe' in files:
                    bin_path = Path(root) / 'ffmpeg.exe'
                    print(f"Found ffmpeg.exe at: {bin_path}")
                    return bin_path.parent
            raise FileNotFoundError("No ffmpeg.exe found in the specified path.")
        except Exception as e:
            print(f"Error finding ffmpeg.exe: {e}")
            return None

    def setup_7zr(self) -> Optional[str]:
        """Set up 7zr.exe either from user input or download.
        
        Returns:
            Path to 7zr.exe if successful, None if setup fails
        """
        use_own_7zr = input("Do you want to provide your own version of 7zr.exe? (yes/no): ").strip().lower()
        
        if use_own_7zr == 'yes':
            sevens_zip_path = input("Please enter the path to your 7zr.exe file: ").strip()
            if os.path.isfile(sevens_zip_path):
                print(f"Using provided 7zr.exe at {sevens_zip_path}.")
                return sevens_zip_path
            print("The specified 7zr.exe file does not exist.")
            return None
            
        if not os.path.isfile(self.config.SEVEN_ZIP_EXEC):
            try:
                self.downloader.download_file(self.config.SEVEN_ZIP_URL, self.config.SEVEN_ZIP_EXEC)
            except requests.exceptions.RequestException as e:
                print(f"Failed to download 7zr.exe: {e}")
                return None
        else:
            print("7zr.exe already exists, skipping download.")
            
        return self.config.SEVEN_ZIP_EXEC

    def setup_ffmpeg(self, seven_zip_exec: str) -> Optional[Path]:
        """Set up FFmpeg either from user input or download.
        
        Args:
            seven_zip_exec: Path to 7zr.exe for extraction
            
        Returns:
            Path to FFmpeg bin directory if successful, None if setup fails
        """
        use_own_ffmpeg = input("Do you already have FFmpeg? (yes/no): ").strip().lower()
        
        if use_own_ffmpeg == 'yes':
            use_system_ffmpeg = input("Do you want to use the system default FFmpeg? (yes/no): ").strip().lower()
            if use_system_ffmpeg == 'yes':
                return None
                
            ffmpeg_path = input("Please enter the path to your FFmpeg bin folder: ").strip()
            if os.path.isdir(ffmpeg_path):
                ffmpeg_bin = self.find_ffmpeg_bin_path(Path(ffmpeg_path))
                return ffmpeg_bin if ffmpeg_bin else None
            print("The specified FFmpeg folder does not exist.")
            return None
            
        if not self.config.FFMPEG_ROOT_PATH.is_dir():
            try:
                self.downloader.download_file(self.config.FFMPEG_URL, self.config.FFMPEG_ARCHIVE)
                self.downloader.extract_7z(self.config.FFMPEG_ARCHIVE, str(self.config.FFMPEG_ROOT_PATH), seven_zip_exec)
                os.remove(self.config.FFMPEG_ARCHIVE)
                return self.find_ffmpeg_bin_path(self.config.FFMPEG_ROOT_PATH)
            except (requests.exceptions.RequestException, subprocess.CalledProcessError) as e:
                print(f"Failed to set up FFmpeg: {e}")
                return None
        else:
            print("FFmpeg folder already exists, skipping download.")
            return self.find_ffmpeg_bin_path(self.config.FFMPEG_ROOT_PATH)

    def setup_ytdlp(self) -> Optional[Path]:
        """Set up yt-dlp either from user input or download.
        
        Returns:
            Path to yt-dlp directory if successful, None if setup fails
        """
        use_own_ytdlp = input("Do you already have yt-dlp? (yes/no): ").strip().lower()
        
        if use_own_ytdlp == 'yes':
            use_system_ytdlp = input("Do you want to use the system default yt-dlp? (yes/no): ").strip().lower()
            if use_system_ytdlp == 'yes':
                return None
                
            ytdlp_path = input("Please enter the path to your yt-dlp folder: ").strip()
            if os.path.isdir(ytdlp_path):
                return Path(ytdlp_path)
            print("The specified yt-dlp folder does not exist.")
            return None
            
        if not self.config.YTDLP_PATH.is_dir():
            try:
                self.downloader.download_file(self.config.YTDLP_URL, self.config.YTDLP_ARCHIVE)
                self.downloader.extract_zip(self.config.YTDLP_ARCHIVE, str(self.config.YTDLP_PATH))
                os.remove(self.config.YTDLP_ARCHIVE)
                return self.config.YTDLP_PATH
            except (requests.exceptions.RequestException, zipfile.BadZipFile) as e:
                print(f"Failed to set up yt-dlp: {e}")
                return None
        else:
            print("yt-dlp folder already exists, skipping download.")
            return self.config.YTDLP_PATH

    def create_config_file(self, ffmpeg_path: Optional[Path], ytdlp_path: Optional[Path]) -> None:
        """Create the batch file for setting PATH environment variable.
        
        Args:
            ffmpeg_path: Path to FFmpeg bin directory
            ytdlp_path: Path to yt-dlp directory
        """
        path_string = ""
        if ffmpeg_path:
            path_string += f"{ffmpeg_path};"
        if ytdlp_path:
            path_string += f"{ytdlp_path};"

        config_content = f'''@echo off
:: Set Global Path Temporary
set "PATH={path_string}%PATH%"
echo PATH updated in this session.
'''
        with open(self.config.CONFIG_FILE, 'w') as file:
            file.write(config_content)
        print(f"{self.config.CONFIG_FILE} created with path settings.")

    def run(self) -> None:
        """Run the environment setup process."""
        print("This script will download the following tools:")
        print("1. FFmpeg: A multimedia framework for processing audio and video files.")
        print("2. yt-dlp: A video downloader for YouTube and other sites.")
        print("3. 7zr: A tool for extracting .7z files.")

        seven_zip_exec = self.setup_7zr()
        if not seven_zip_exec:
            print("Failed to set up 7zr.exe. Exiting...")
            return

        ffmpeg_path = self.setup_ffmpeg(seven_zip_exec)
        ytdlp_path = self.setup_ytdlp()
        
        self.create_config_file(ffmpeg_path, ytdlp_path)


def check_system_compatibility() -> bool:
    """Check if the current system is compatible with this script.
    
    Returns:
        True if system is compatible, False otherwise
    """
    system = platform.system()
    
    if system == "Windows":
        version_info = platform.version().split('.')
        major_version = int(version_info[0])
        
        if major_version >= 10:
            return True
        print("This script is for Windows 10 or newer only.")
        return False
        
    print(f"This script isn't compatible with {system} yet.")
    return False


def main() -> None:
    """Main entry point of the script."""
    print("Version 0.0.34")

    if os.path.exists("ffmpeg_path.bat"):
        print("Config file already exists. Exiting...")
        return

    if not check_system_compatibility():
        sys.exit(1)

    setup = EnvironmentSetup()
    setup.run()


if __name__ == "__main__":
    main()