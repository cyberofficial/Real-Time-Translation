"""
Module for displaying project information and credits.

This module provides functionality to display information about the project,
including the creator, license, repository link, and contributors. It uses
colorama for colored terminal output.
"""

from colorama import Fore, Style
import sys

def contributors(ScriptCreator, GitHubRepo):
    """
    Display project information and contributor credits.

    Prints formatted information about the project including the creator,
    license, GitHub repository, and a list of contributors. Uses colored
    output for better visibility and exits the program after display.

    Args:
        ScriptCreator (str): Name of the project creator
        GitHubRepo (str): URL of the project's GitHub repository

    Note:
        This function calls sys.exit() after displaying the information.
    """
    print(f"\033[4m{Fore.GREEN}About the project:{Style.RESET_ALL}\033[0m")
    print(f"This project was created by \033[4m{Fore.GREEN}{ScriptCreator}{Style.RESET_ALL}\033[0m and is licensed under the \033[4m{Fore.GREEN}GPLv3{Style.RESET_ALL}\033[0m license.\n\nYou can find the source code at \033[4m{Fore.GREEN}{GitHubRepo}{Style.RESET_ALL}\033[0m.\nBased on Whisper from OpenAI at \033[4m{Fore.GREEN}https://github.com/openai/whisper{Style.RESET_ALL}\033[0m.\n\n\n\n")
    # contributors #
    print(f"\033[4m{Fore.GREEN}Contributors:{Style.RESET_ALL}\033[0m")
    print("@DaniruKun from https://watsonindustries.live")
    print("[Expletive Deleted] https://evitelpxe.neocities.org")
    sys.exit()

print("About Module Loaded")