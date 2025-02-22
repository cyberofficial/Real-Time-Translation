"""
Audio handling module for microphone input and calibration.

This module provides functionality for handling microphone input, including
recording callbacks and microphone calibration. It uses the speech_recognition
library for audio processing and colorama for formatted console output.
"""

import speech_recognition as sr
from queue import Queue
from colorama import Fore, Style

def record_callback(_, audio: sr.AudioData, data_queue: Queue) -> None:
    """
    Callback function for processing recorded audio data.

    This function is called whenever new audio data is available. It extracts
    the raw audio data and puts it into a queue for further processing.

    Args:
        _ : Unused recognizer instance
        audio (sr.AudioData): The recorded audio data
        data_queue (Queue): Queue to store the raw audio data

    Returns:
        None
    """
    data = audio.get_raw_data()
    data_queue.put(data)

def mic_calibration(recorder: sr.Recognizer, source: sr.Microphone, calibration_time: int):
    """
    Calibrate microphone by adjusting for ambient noise.

    Performs microphone calibration by measuring ambient noise levels and
    adjusting the energy threshold accordingly.

    Args:
        recorder (sr.Recognizer): Speech recognizer instance
        source (sr.Microphone): Microphone source to calibrate
        calibration_time (int): Duration in seconds for calibration

    Returns:
        None
    """
    print("Starting mic calibration...")
    with source as s:
        recorder.adjust_for_ambient_noise(s, duration=calibration_time)
    reset_text = Style.RESET_ALL
    print(f"Calibration complete. The microphone is set to: {Fore.YELLOW}" + str(recorder.energy_threshold) + f"{reset_text}")

def handle_mic_calibration(recorder: sr.Recognizer, source: sr.Microphone, args):
    """
    Handle the complete microphone calibration process with user interaction.

    Manages the calibration workflow including user prompts and recalibration
    options. Allows users to recalibrate until they are satisfied with the
    settings.

    Args:
        recorder (sr.Recognizer): Speech recognizer instance
        source (sr.Microphone): Microphone source to calibrate
        args: Command line arguments containing calibration settings

    Returns:
        None
    """
    reset_text = Style.RESET_ALL
    if args.mic_calibration_time:
        print("Mic calibration flag detected.\n")
        print(f"Press {Fore.YELLOW}[enter]{reset_text} when ready to start mic calibration.\nMake sure there is no one speaking during this time.")
        if args.mic_calibration_time == 0:
            args.mic_calibration_time = 5
            mic_calibration(recorder, source, args.mic_calibration_time)
        else:
            print("Waiting for user input...")
            input()
            mic_calibration(recorder, source, args.mic_calibration_time)
            print(f"If you are happy with this setting press {Fore.YELLOW}[enter]{reset_text} or type {Fore.YELLOW}[r]{reset_text} then {Fore.YELLOW}[enter]{reset_text} to recalibrate.\n")
            while True:
                user_input = input("r/enter: ")
                if user_input == "r":
                    mic_calibration(recorder, source, args.mic_calibration_time)
                    print(f"If you are happy with this setting press {Fore.YELLOW}[enter]{reset_text} or type {Fore.YELLOW}[r]{reset_text} then {Fore.YELLOW}[enter]{reset_text} to recalibrate.\n")
                else:
                    break