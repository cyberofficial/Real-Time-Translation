"""
File handling module for managing files and directories.

This module provides utilities for file operations including:
- Managing blacklist files
- Handling temporary directories for audio processing
- Saving transcription results
- Error logging and reporting
"""

import os
from datetime import datetime
from modules.discord import send_to_discord_webhook

def load_blacklist(filename):
    """
    Load and parse the blacklist file.

    Reads a text file containing blacklisted terms or phrases, with each entry
    on a new line.

    Args:
        filename (str): Path to the blacklist file (.txt format)

    Returns:
        list: List of blacklisted terms

    Raises:
        ValueError: If the file extension is not .txt
    """
    if not filename.endswith(".txt"):
        raise ValueError("Blacklist file must be in .txt format.")

    blacklist = []
    try:
        with open(filename, "r", encoding="utf-8") as f:
            for line in f:
                blacklist.append(line.strip())
    except FileNotFoundError:
        print(f"Warning: Blacklist file '{filename}' not found.")
    return blacklist

def setup_temp_directory():
    """
    Set up temporary directory for audio files.

    Creates a 'temp' directory if it doesn't exist, used for storing
    temporary audio files during processing.

    Returns:
        str: Path to the temporary directory
    """
    if not os.path.exists("temp"):
        os.makedirs("temp")
    return "temp"

def clean_temp_directory(temp_dir):
    """
    Clean temporary directory of non-recording files.

    Removes all files in the temporary directory that don't start with 'rec_',
    which are used to identify active recording files.

    Args:
        temp_dir (str): Path to the temporary directory
    """
    try:
        for file in os.listdir(temp_dir):
            if not file.startswith("rec_"):
                os.remove(os.path.join(temp_dir, file))
    except Exception:
        pass

def save_transcript(transcription, args):
    """
    Save transcription to a file.

    Saves the transcription results including original text, translations,
    and transcriptions to a text file. Creates numbered files if multiple
    transcriptions exist.

    Args:
        transcription (list): List of tuples containing (original_text,
            translated_text, transcribed_text, detected_language)
        args: Command line arguments containing output directory settings
    """
    if not args.output:
        out = "out"
    else:
        out = args.output
    
    if not os.path.isdir(out):
        os.mkdir(out)

    transcript = os.path.join(os.getcwd(), out, 'transcription.txt')
    if os.path.isfile(transcript):
        transcript = os.path.join(os.getcwd(), out, 'transcription_' + str(len(os.listdir(out))) + '.txt')
    
    with open(transcript, 'w', encoding='utf-8') as transcription_file:
        for original_text, translated_text, transcribed_text, detected_language in transcription:
            transcription_file.write(f"-=-=-=-=-=-=-=-\nOriginal ({detected_language}): {original_text}\n")
            if translated_text:
                transcription_file.write(f"Translation: {translated_text}\n")
            if transcribed_text:
                transcription_file.write(f"Transcription: {transcribed_text}\n")
    
    print(f"Transcription was saved to {transcript}")

def handle_error(e, webhook_url=None):
    """
    Handle and log errors.

    Logs errors to a file and optionally sends them to a Discord webhook.
    Handles keyboard interrupts differently from other errors.

    Args:
        e (Exception): The error to handle
        webhook_url (str, optional): Discord webhook URL for error reporting

    Returns:
        bool: True if the error was a KeyboardInterrupt, False otherwise
    """
    if not isinstance(e, KeyboardInterrupt):
        print(e)
        if os.path.isfile('error_report.txt'):
            mode = 'a'
        else:
            mode = 'w'
        
        with open('error_report.txt', mode) as error_report_file:
            error_report_file.write(str(e))
            
        if webhook_url:
            send_to_discord_webhook(webhook_url, f"Error occurred: {str(e)}")
    return isinstance(e, KeyboardInterrupt)