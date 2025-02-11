"""
Device management module for audio input and processing devices.

This module handles the configuration and management of both audio input devices
(microphones) and processing devices (CPU/CUDA). It provides functionality for:
- Detecting and selecting microphone devices
- Managing CUDA device selection for GPU processing
- Validating device configurations
- Listing available audio devices
"""

import torch
import speech_recognition as sr
import pyaudio
from prettytable import PrettyTable
from colorama import Fore, Style
import sys

def is_input_device(device_index):
    """
    Check if the device at given index is a valid input device.

    Args:
        device_index (int): Index of the audio device to check

    Returns:
        bool: True if device is an input device, False otherwise
    """
    pa = pyaudio.PyAudio()
    device_info = pa.get_device_info_by_index(device_index)
    return device_info['maxInputChannels'] > 0

def get_microphone_source(args):
    """
    Get microphone sources based on provided command line arguments.

    Attempts to find and configure two separate microphone sources based on the provided
    arguments. Falls back to system default if no specific microphone is specified.

    Args:
        args: Command line arguments containing microphone settings

    Returns:
        tuple: (sr.Microphone, sr.Microphone, str) - Two configured microphone objects and device name

    Raises:
        ValueError: If no valid input devices are found
    """
    pa = pyaudio.PyAudio()
    available_mics = sr.Microphone.list_microphone_names()
    device_index = None
    mic_name = "system default"

    if args.set_microphone:
        mic_name = args.set_microphone

        if mic_name.isdigit():
            mic_index = int(mic_name)
            if mic_index in range(len(available_mics)) and is_input_device(mic_index):
                device_index = mic_index
                mic_name = available_mics[mic_index]
            else:
                print("Invalid audio source. Please choose a valid microphone.")
                sys.exit(0)
        else:
            for index, name in enumerate(available_mics):
                if mic_name == name and is_input_device(index):
                    device_index = index
                    break

    if device_index is None:
        for index in range(pa.get_device_count()):
            if is_input_device(index):
                device_index = index
                break

    if device_index is None:
        raise ValueError("No valid input devices found.")

    # Create two separate microphone instances with the same settings
    source_calibration = sr.Microphone(sample_rate=16000, device_index=device_index)
    source_listening = sr.Microphone(sample_rate=16000, device_index=device_index)
    
    return source_calibration, source_listening, mic_name

def list_microphones():
    """
    List all available microphone devices in a formatted table.

    Displays a table of available microphone devices with their indices and names.
    Only shows devices that are valid input devices.
    Exits the program after displaying the list.
    """
    print("Available microphone devices are: ")
    mic_table = PrettyTable()
    mic_table.field_names = ["Index", "Microphone Name"]

    for index, name in enumerate(sr.Microphone.list_microphone_names()):
        if is_input_device(index):
            mic_table.add_row([index, name])

    print(mic_table)
    reset_text = Style.RESET_ALL
    input(f"Press {Fore.YELLOW}[enter]{reset_text} to exit.")
    sys.exit(0)

def setup_device(args):
    """
    Set up and configure the processing device (CPU/CUDA).

    Configures the processing device based on availability and user preferences.
    Handles CUDA device selection when multiple GPUs are available.

    Args:
        args: Command line arguments containing device preferences

    Returns:
        torch.device: Configured processing device

    Note:
        Prints relevant device information including VRAM availability for CUDA devices.
    """
    if args.device:
        device = torch.device(args.device)
    else:
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        if args.device == "cuda" and not torch.cuda.is_available():
            print("WARNING: CUDA was chosen but it is not available. Falling back to CPU.")
    print(f"Using device: {device}")

    if device.type == "cuda":
        cuda_device_count = torch.cuda.device_count()
        if cuda_device_count > 1 and args.cuda_device == 0:
            selected_device = select_cuda_device(cuda_device_count)
        else:
            selected_device = args.cuda_device

        torch.cuda.set_device(selected_device)
        print(f"CUDA device name: {torch.cuda.get_device_name(torch.cuda.current_device())}")
        print(f"VRAM available: {torch.cuda.get_device_properties(torch.cuda.current_device()).total_memory / 1024 / 1024} MB")

    return device

def select_cuda_device(cuda_device_count):
    """
    Interactive CUDA device selection when multiple devices are available.

    Presents a list of available CUDA devices with their names and VRAM,
    allowing the user to select a specific device.

    Args:
        cuda_device_count (int): Number of available CUDA devices

    Returns:
        int: Index of the selected CUDA device

    Note:
        Continues prompting until a valid device is selected.
    """
    while True:
        print("Multiple CUDA devices detected. Please choose a device:")
        for i in range(cuda_device_count):
            print(f"{i}: {torch.cuda.get_device_name(i)}, VRAM: {torch.cuda.get_device_properties(i).total_memory / 1024 / 1024} MB")
        try:
            selected_device = int(input("Enter the device number: "))
            if 0 <= selected_device < cuda_device_count:
                return selected_device
            else:
                print("Invalid device number. Please try again.")
        except ValueError:
            print("Invalid input. Please enter a valid device number.")