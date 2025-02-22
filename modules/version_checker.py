"""
Version Checker Module

This module provides functionality to check and compare version numbers between
local and remote instances of the application. It supports semantic versioning
with major.minor.patch format.

Features:
- Remote version checking from GitHub repository
- Semantic version comparison (major, minor, patch)
- Colored output for better readability
- Detailed error handling for various HTTP status codes
- User-friendly update notifications

The module uses GitHub's raw content URLs to fetch the remote version and
provides appropriate feedback for various network conditions and version
mismatches.
"""

import requests
import re
from typing import Optional
from colorama import Fore, Style

version = "1.1.0"
ScriptCreator = "cyberofficial"
GitHubRepo = "https://github.com/cyberofficial/Synthalingua"
repo_owner = "cyberofficial"
repo_name = "Synthalingua"

def get_remote_version(repo_owner: str, repo_name: str, updatebranch: str, file_path: str) -> Optional[str]:
    """
    Fetch and extract version number from a file in a GitHub repository.

    Args:
        repo_owner (str): GitHub repository owner username
        repo_name (str): Name of the GitHub repository
        updatebranch (str): Branch name to check for updates
        file_path (str): Path to the file containing version information

    Returns:
        Optional[str]: Version string if found and successfully retrieved,
                      None if any error occurs (network, parsing, etc.)

    The function handles various HTTP error cases with appropriate user feedback:
    - 200: Success, attempts to parse version
    - 404: File not found
    - 500: Internal server error
    - 502: Bad gateway
    - 503: Service unavailable
    - 504: Gateway timeout
    Other status codes result in a generic error message
    """
    url = f"https://raw.githubusercontent.com/{repo_owner}/{repo_name}/{updatebranch}/{file_path}"
    response = requests.get(url)

    # if the response failed then return None
    if response.status_code != 200:
        print(f"{Fore.RED}An error occurred when checking for updates. Status code: {response.status_code}{Style.RESET_ALL}")
        print(f"Could not fetch remote version from: {Fore.YELLOW}{url}{Style.RESET_ALL}")
        print(f"Please check your internet connection and try again.")
        print("\n\n")
        return None

    if response.status_code == 200:
        remote_file_content = response.text
        version_search = re.search(r'version\s*=\s*"([\d.]+)"', remote_file_content)
        if version_search:
            remote_version = version_search.group(1)
            return remote_version
        else:
            print(f"{Fore.RED}Error: Version not found in the remote file.{Style.RESET_ALL}")
            return None
    if response.status_code == 404:
        print(f"{Fore.RED}Error: The file was not found on the remote repository.{Style.RESET_ALL}")
        return None
    if response.status_code == 503:
        print(f"{Fore.RED}Error: The server is temporarily unavailable.{Style.RESET_ALL}")
        return None
    if response.status_code == 502:
        print(f"{Fore.RED}Error: Bad gateway.{Style.RESET_ALL}")
        return None
    if response.status_code == 504:
        print(f"{Fore.RED}Error: Gateway timeout.{Style.RESET_ALL}")
        return None
    if response.status_code == 500:
        print(f"{Fore.RED}Error: Internal server error.{Style.RESET_ALL}")
        return None
    else:
        print(f"{Fore.RED}An error occurred when checking for updates. Status code: {response.status_code}{Style.RESET_ALL}")
        print(f"Could not fetch remote version from: {Fore.YELLOW}{url}{Style.RESET_ALL}")
        print(f"Please check your internet connection and try again.")
        print("\n\n")
        # return with None to indicate an error
        return None
        

def check_for_updates(updatebranch: str) -> None:
    """
    Check and compare local version against remote version from GitHub.

    Args:
        updatebranch (str): Branch name to check for updates (e.g., 'main', 'master')

    This function performs semantic version comparison following major.minor.patch format:
    1. First compares major version numbers
    2. If major versions match, compares minor version numbers
    3. If minor versions match, compares patch version numbers

    Output includes:
    - Version mismatch notifications (major, minor, or patch level)
    - Update recommendations with GitHub repository link
    - Confirmation when using latest version
    - Notification if local version is newer than remote

    The function uses colored output for better readability:
    - Yellow: Version numbers
    - Red: Error messages
    Standard output for status messages
    """
    local_version = version
    remote_version = get_remote_version(repo_owner, repo_name, updatebranch, "modules/version_checker.py")

    # if the response failed then return None
    if remote_version is None:
        return

    if remote_version is not None:
        # Split the version numbers into parts (major, minor, patch)
        local_version_parts = [int(part) for part in local_version.split(".")]
        remote_version_parts = [int(part) for part in remote_version.split(".")]

        # Compare major versions
        if remote_version_parts[0] > local_version_parts[0]:
            print(f"Major version mismatch. Local version: {Fore.YELLOW}{local_version}{Style.RESET_ALL}, remote version: {Fore.YELLOW}{remote_version}{Style.RESET_ALL}")
            print("Consider updating to the latest version.")
            print(f"Update available at: {GitHubRepo}")
            print("\n\n")
        elif remote_version_parts[0] == local_version_parts[0]:
            # Compare minor versions
            if remote_version_parts[1] > local_version_parts[1]:
                print(f"Minor version mismatch. Local version: {Fore.YELLOW}{local_version}{Style.RESET_ALL}, remote version: {Fore.YELLOW}{remote_version}{Style.RESET_ALL}")
                print("Consider updating to the latest version.")
                print(f"Update available at: {GitHubRepo}")
                print("\n\n")
            elif remote_version_parts[1] == local_version_parts[1]:
                # Compare patch versions
                if remote_version_parts[2] > local_version_parts[2]:
                    print(f"Patch version mismatch. Local version: {Fore.YELLOW}{local_version}{Style.RESET_ALL}, remote version: {Fore.YELLOW}{remote_version}{Style.RESET_ALL}")
                    print("Consider updating to the latest version.")
                    print(f"Update available at: {GitHubRepo}")
                    print("\n\n")
                else:
                    print("You are already using the latest version.")
                    print(f"Current version: {local_version}")
                    print("\n\n")
            else:
                print("You are already using a newer version.")
                print(f"Current version: {local_version}")
                print("\n\n")
        else:
            print("You are already using a newer version.")
            print(f"Current version: {local_version}")
            print("\n\n")

print("Version Checker Module Loaded")
