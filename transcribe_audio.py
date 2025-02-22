import sys
import os
import torch
import speech_recognition as sr
import whisper
from queue import Queue
from tempfile import NamedTemporaryFile
from colorama import Fore, Style, init

from modules.audio_handlers import record_callback, handle_mic_calibration
from modules.device_manager import get_microphone_source, list_microphones, setup_device
from modules.file_handlers import load_blacklist, setup_temp_directory, clean_temp_directory, save_transcript, handle_error
from modules.transcription_core import TranscriptionCore
from modules.stream_handler import handle_stream_setup
from modules.stream_transcription_module import stop_transcription
from modules import parser_args
from modules.languages import get_valid_languages
from modules import api_backend
from modules.version_checker import check_for_updates
from modules.discord import send_to_discord_webhook
from modules.about import contributors
from modules.sub_gen import run_sub_gen

init()


def main():
    args = parser_args.parse_arguments()

    # Early exit conditions
    if len(sys.argv) == 1:
        print("No arguments provided. Please run the script with the --help flag to see a list of available arguments.")
        sys.exit(1)

    if args.about:
        from modules.version_checker import ScriptCreator, GitHubRepo
        contributors(ScriptCreator, GitHubRepo)

    # Check input sources
    if args.stream is None and args.microphone_enabled is None and not args.makecaptions:
        print("No audio source was set. Please set an audio source.")
        reset_text = Style.RESET_ALL
        input(f"Press {Fore.YELLOW}[enter]{reset_text} to exit.")
        sys.exit("Exiting...")

    if args.stream is not None and args.microphone_enabled is not None:
        print("You can only use one input source. Please only set one input source.")
        reset_text = Style.RESET_ALL
        input(f"Press {Fore.YELLOW}[enter]{reset_text} to exit.")
        sys.exit("Exiting...")

    if args.stream_transcribe and args.stream_target_language is None:
        print("Stream Transcribe is set but no stream target language is set. Please set a stream target language.")
        sys.exit("Exiting...")

    # Load blacklist
    blacklist = []
    if args.ignorelist:
        print(f"Loaded word filtering list from: {args.ignorelist}")
        blacklist = load_blacklist(args.ignorelist)
        if blacklist:
            print(f"Loaded blacklist: {blacklist}")

    # Check for updates
    if args.updatebranch != "disable":
        print("\nChecking for updates...")
        try:
            check_for_updates(args.updatebranch)
        except Exception as e:
            print(f"Error checking for updates: {str(e)}")
            print("Continuing with script...\n\n")

    # Initialize recording components
    data_queue = Queue()
    recorder = sr.Recognizer()
    recorder.energy_threshold = args.energy_threshold
    recorder.dynamic_energy_threshold = False

    # Handle microphone listing
    if args.list_microphones:
        list_microphones()

    # Set up device (CPU/CUDA)
    device = setup_device(args)

    # Set up audio source
    source_calibration = None
    source_listening = None
    if args.microphone_enabled:
        try:
            source_calibration, source_listening, mic_name = get_microphone_source(args)
            handle_mic_calibration(recorder, source_calibration, args)
        except ValueError as e:
            print("Error: Unable to initialize microphone. Check your microphone settings and permissions.")
            print(f"Error details: {str(e)}")
            sys.exit(1)

    # Validate languages
    valid_languages = get_valid_languages()
    if args.language and args.language not in valid_languages:
        print("Invalid language. Please choose a valid language from the list below:")
        print(valid_languages)
        return

    if args.transcribe and not args.target_language:
        print("Transcribe is set but no target language is set. Please set a target language.")
        return
    elif args.transcribe and args.target_language not in valid_languages:
        print("Invalid target language. Please choose a valid language from the list below:")
        print(valid_languages)
        return

    # Adjust phrase timeout for Discord webhook
    if args.microphone_enabled and args.phrase_timeout > 1 and args.discord_webhook:
        print(f"{Fore.RED}WARNING{Style.RESET_ALL}: phrase_timeout is set to {args.phrase_timeout} seconds. Setting to 1 second to avoid multiple webhook messages.")
        args.phrase_timeout = 1

    # Set up model directory
    if not os.path.exists(args.model_dir):
        print("Creating models folder...")
        os.makedirs(args.model_dir)

    # Configure model
    model = parser_args.set_model_by_ram(args.ram, args.language)
    if not args.makecaptions:
        audio_model = whisper.load_model(model, device=device, download_root=args.model_dir)

    # Set up API backend if needed
    if args.portnumber:
        print("Port number was set, so spinning up a web server...")
        api_backend.flask_server(operation="start", portnumber=args.portnumber)

    # Set up temporary directory
    temp_dir = setup_temp_directory()
    temp_file = NamedTemporaryFile(dir=temp_dir, delete=not args.keep_temp, suffix=".ts", prefix="rec_").name

    # Initialize webhook
    webhook_url = args.discord_webhook if args.discord_webhook else None
    if webhook_url:
        message = "Transcription started." + (" Translation enabled." if args.translate else " Translation disabled.")
        message += f"\nUsing the {args.ram} ram model."
        send_to_discord_webhook(webhook_url, message)

    # Handle caption generation
    if args.makecaptions:
        if args.file_output_name is None:
            args.file_output_name = "filename"
        run_sub_gen(args.file_input, args.file_output_name, args.file_output)
        print("Press enter to exit...")
        input()
        sys.exit("Exiting...")

    # Set up stream if needed
    stream_thread = None
    if args.stream:
        print(f"Stream mode enabled. Using stream: {args.stream}")
        stream_thread = handle_stream_setup(args, audio_model, temp_dir, webhook_url)
    
    # Start microphone listening if enabled
    if args.microphone_enabled:
        try:
            print(f"Microphone set to: {mic_name}")
            # Set up background listening without context manager
            recorder.listen_in_background(source_listening, lambda r, a: record_callback(r, a, data_queue),
                                    phrase_time_limit=args.record_timeout)
        except AssertionError as e:
            print("Error: Unable to initialize microphone. Check your microphone settings and permissions.")
            print(f"Error details: {str(e)}")
            sys.exit(1)

    print("Model loaded.\n")
    print(f"Using {model} model.")

    if device.type == "cuda" and "AMD" in torch.cuda.get_device_name(torch.cuda.current_device()):
        print("WARNING: You are using an AMD GPU with CUDA. This may not work properly. Consider using CPU instead.")

    # Initialize transcription core
    args.model = model  # Add the model name to args
    transcription_core = TranscriptionCore(args, device, audio_model, blacklist)

    try:
        # Main processing loop
        while True:
            if not transcription_core.process_audio(data_queue, source_listening, temp_file):
                break

    except KeyboardInterrupt:
        print("Exiting...")
        if args.stream:
            stop_transcription()
            clean_temp_directory(temp_dir)
        
        if webhook_url:
            send_to_discord_webhook(webhook_url, "**Service has stopped.**")
        
        if args.save_transcript:
            save_transcript(transcription_core.transcription, args)
            
        if args.portnumber:
            api_backend.kill_server()
            
        sys.exit(0)

    except Exception as e:
        is_keyboard_interrupt = handle_error(e, webhook_url)
        if is_keyboard_interrupt:
            sys.exit(0)

if __name__ == "__main__":
    main()