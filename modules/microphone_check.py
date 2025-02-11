"""
Microphone verification module.

This module provides functionality to verify the presence and basic
functionality of a microphone by testing ambient noise detection.
It uses the speech_recognition library to perform the verification.
"""

import speech_recognition as sr
from speech_recognition.__main__ import r

def microphone_check():
    """
    Verify microphone availability and functionality.

    Performs a basic check to ensure that:
    1. A microphone is present in the system
    2. The microphone can be accessed
    3. Basic ambient noise calibration can be performed

    Returns:
        bool: True if microphone check is successful
              (Note: Currently always returns True if no exceptions occur)

    Raises:
        Various exceptions from speech_recognition if microphone
        initialization or access fails
    """
    # Check if the user has a microphone
    print("Checking for microphone...")
    mic = sr.Microphone()
    with mic as source:
        r.adjust_for_ambient_noise(source)
    print("Microphone check complete.")
    print("\n\n")
    return True

print("Microphone Check Module Loaded")
