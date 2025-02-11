"""
Console window management module for cross-platform terminal customization.

This module provides functionality to modify console window properties,
specifically the window title, across different operating systems (Windows and Unix-like).
It handles platform-specific implementations for setting console window titles.
"""

import sys
import ctypes

def set_window_title(detected_language, confidence, model):
    """
    Set the console window title with current transcription information.

    Updates the console window title to display the current model being used,
    the detected language, and the confidence level of the language detection.
    Handles both Windows and Unix-like systems differently.

    Args:
        detected_language (str): The detected language of the audio
        confidence (float): Confidence percentage of language detection
        model (str): Name of the model being used for transcription

    Example:
        set_window_title("English", 95.5, "base")
        # Sets title to "Model: base - English [95.50%]"
    """
    title = f"Model: {model} - {detected_language} [{confidence:.2f}%]"

    if sys.platform == "win32":
        ctypes.windll.kernel32.SetConsoleTitleW(title)
    else:
        sys.stdout.write(f"]2;{title}")
        sys.stdout.flush()

print("Console Settings Module Loaded")