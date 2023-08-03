import argparse
import io
import os
import speech_recognition as sr
import whisper
import torch
import math
import sys
import ctypes
import shutil
import numpy as np
import requests
import json
import re
try:
    # if the os is not windows then skip this
    if os.name == 'nt':
        import sys, win32api
        win32api.SetDllDirectory(sys._MEIPASS)
except:
    pass
import pytz
import pyaudio
import humanize
import humanize

from datetime import datetime, timedelta
from queue import Queue
from tempfile import NamedTemporaryFile
from time import sleep
from sys import platform
from colorama import Fore, Back, Style, init
from tqdm import tqdm
from datetime import datetime
from numba import cuda
from prettytable import PrettyTable
from dateutil.tz import tzlocal
from tzlocal import get_localzone
init()

try:
    cuda_available = torch.cuda.is_available()
except:
    cuda_available = False

print("Loading Modules...")
from modules.version_checker import check_for_updates
from modules.model_downloader import fine_tune_model_dl, fine_tune_model_dl_compressed
from modules.discord import send_to_discord_webhook
from modules.console_settings import set_window_title
from modules.warnings import print_warning
from modules import parser_args
from modules.languages import get_valid_languages
print("Modules Loaded\n\n")

# Code is semi documented, but if you have any questions, feel free to ask in the Discussions tab.

def main():
    args = parser_args.parse_arguments()

    # if args.updatebranch is set as disable then skip
    if args.updatebranch != "disable":
        check_for_updates(args.updatebranch)

    def record_callback(_, audio:sr.AudioData) -> None:
        data = audio.get_raw_data()
        data_queue.put(data)

    def is_input_device(device_index):
        pa = pyaudio.PyAudio()
        device_info = pa.get_device_info_by_index(device_index)
        return device_info['maxInputChannels'] > 0

    def get_microphone_source(args):
        pa = pyaudio.PyAudio()
        available_mics = sr.Microphone.list_microphone_names()

        def is_input_device(device_index):
            device_info = pa.get_device_info_by_index(device_index)
            return device_info['maxInputChannels'] > 0

        if args.set_microphone:
            mic_name = args.set_microphone

            if mic_name.isdigit():
                mic_index = int(mic_name)
                if mic_index in range(len(available_mics)) and is_input_device(mic_index):
                    return sr.Microphone(sample_rate=16000, device_index=mic_index), available_mics[mic_index]
                else:
                    print("Invalid audio source. Please choose a valid microphone.")
                    sys.exit(0)
            else:
                for index, name in enumerate(available_mics):
                    if mic_name == name and is_input_device(index):
                        return sr.Microphone(sample_rate=16000, device_index=index), name

        for index in range(pa.get_device_count()):
            if is_input_device(index):
                return sr.Microphone(sample_rate=16000, device_index=index), "system default"

        raise ValueError("No valid input devices found.")

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)

    if args.about:
        from modules.about import contributors
        from modules.version_checker import ScriptCreator, GitHubRepo
        contributors(ScriptCreator, GitHubRepo)


    model = parser_args.set_model_by_ram(args.ram, args.language)

    hardmodel = None

    if args.ramforce:
        hardmodel = args.ram

    phrase_time = None
    last_sample = bytes()
    data_queue = Queue()
    recorder = sr.Recognizer()
    recorder.energy_threshold = args.energy_threshold
    recorder.dynamic_energy_threshold = False
    
    valid_languages = get_valid_languages()

    if args.language:
        if args.language not in valid_languages:
            print("Invalid language. Please choose a valid language from the list below:")
            print(valid_languages)
            return

    # check if transcribed is set as an argument if so check if target language is set, if tagret language is not set then exit saying need target language
    if args.transcribe:
        if not args.target_language:
            print("Transcribe is set but no target language is set. Please set a target language.")
            return
        else:
            if args.target_language not in valid_languages:
                print("Invalid target language. Please choose a valid language from the list below:")
                print(valid_languages)
                return
        target_language = args.target_language
    
    if args.phrase_timeout > 1 and args.discord_webhook:
        red_text = Fore.RED + Back.BLACK
        print(f"{red_text}WARNING{reset_text}: phrase_timeout is set to {args.phrase_timeout} seconds. This will cause the webhook to send multiple messages. Setting phrase_timeout to 1 second to avoid this.")
        args.phrase_timeout = 1
        
    if args.device:
        device = torch.device(args.device)
    else:
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        if args.device == "cuda" and not torch.cuda.is_available():
            print("WARNING: CUDA was chosen but it is not available. Falling back to CPU.")
    print(f"Using device: {device}")

    if device.type == "cuda":
        # Check if multiple CUDA devices are available
        cuda_device_count = torch.cuda.device_count()
        if cuda_device_count > 1 and args.cuda_device == 0:
            while True:
                print("Multiple CUDA devices detected. Please choose a device:")
                for i in range(cuda_device_count):
                    print(f"{i}: {torch.cuda.get_device_name(i)}, VRAM: {torch.cuda.get_device_properties(i).total_memory / 1024 / 1024} MB")
                try:
                    selected_device = int(input("Enter the device number: "))
                    if 0 <= selected_device < cuda_device_count:
                        break
                    else:
                        print("Invalid device number. Please try again.")
                except ValueError:
                    print("Invalid input. Please enter a valid device number.")
        else:
            selected_device = args.cuda_device

        torch.cuda.set_device(selected_device)
        print(f"CUDA device name: {torch.cuda.get_device_name(torch.cuda.current_device())}")
        print(f"VRAM available: {torch.cuda.get_device_properties(torch.cuda.current_device()).total_memory / 1024 / 1024} MB")

 
    if args.list_microphones:
        print("Available microphone devices are: ")
        mic_table = PrettyTable()
        mic_table.field_names = ["Index", "Microphone Name"]

        for index, name in enumerate(sr.Microphone.list_microphone_names()):
            if is_input_device(index):
                mic_table.add_row([index, name])

        print(mic_table)
        sys.exit(0)

    try:
        source, mic_name = get_microphone_source(args)
    except ValueError as e:
        print(e)
        sys.exit(0)

    with source as s:
        try:
            recorder.adjust_for_ambient_noise(s)
            print(f"Microphone set to: {mic_name}")
        except AssertionError as e:
            print(e)

    if args.language == "en" or args.language == "English":
        model += ".en"
        if model == "large" or model == "large.en":
            model = "large"

    if not os.path.exists("models"):
        print("Creating models folder...")
        os.makedirs("models")

    if device.type == "cuda":
        cuda_vram = torch.cuda.get_device_properties(torch.cuda.current_device()).total_memory / 1024 / 1024
        overhead_buffer = 200

        ram_options = [("12gb", 12000), ("6gb", 6144), ("4gb", 4096), ("2gb", 2048), ("1gb", 1024)]

        found = False
        old_ram_flag = args.ram
        for i, (ram_option, required_vram) in enumerate(ram_options):
            if args.ram == ram_option and cuda_vram < required_vram + overhead_buffer:
                if i + 1 < len(ram_options):
                    args.ram = ram_options[i + 1][0]
                else:
                    args.ram = ram_option
                    device = torch.device("cpu")
                    print("WARNING: CUDA was chosen, but the VRAM available is less than 1 GB. Falling back to CPU.")
                    break
            else:
                found = True
                break

        if not found:
            device = torch.device("cpu")
            print("WARNING: No suitable RAM setting was found. Falling back to CPU.")
        elif old_ram_flag != args.ram:
            print_warning(old_ram_flag, args.ram, required_vram + overhead_buffer, cuda_vram)

    print("Now using ram flag: " + args.ram)

    if args.ram == "1gb" or args.ram == "2gb" or args.ram == "4gb":
        red_text = Style.BRIGHT + Fore.RED
        reset_text = Style.RESET_ALL
        if not os.path.exists("models/fine_tuned_model_compressed_v2.pt"):
            print("Warning - Since you have chosen a low amount of RAM, the fine-tuned model will be downloaded in a compressed format.\nThis will result in a some what faster startup time and a slower inference time, but will also result in slight reduction in accuracy.")
            print("Compressed Fine-tuned model not found. Downloading Compressed fine-tuned model... [Via OneDrive (Public)]")
            fine_tune_model_dl_compressed()
            try:
                if args.use_finetune == True:
                    whisper.load_model("models/fine_tuned_model_compressed_v2.pt", device=device, download_root="models")
                    print("Fine-tuned model loaded into memory.")
                    if device.type == "cuda":
                        max_split_size_mb = 128
            except Exception as e:
                print("Failed to load fine-tuned model. Results may be inaccurate. If you experience issues, please delete the fine-tuned model from the models folder and restart the program. If you still experience issues, please open an issue on GitHub.")
                red_text = Fore.RED + Back.BLACK
                print(f"{red_text}Error: {e}{reset_text}")
                pass
        else:
            try:
                if args.use_finetune == True:
                    whisper.load_model("models/fine_tuned_model_compressed_v2.pt", device=device, download_root="models")
                    print("Fine-tuned model loaded into memory.")
                    if device.type == "cuda":
                        max_split_size_mb = 128
            except Exception as e:
                print("Failed to load fine-tuned model. Results may be inaccurate. If you experience issues, please delete the fine-tuned model from the models folder and restart the program. If you still experience issues, please open an issue on GitHub.")
                red_text = Fore.RED + Back.BLACK
                print(f"{red_text}Error: {e}{reset_text}")
                pass
    else:
        if not os.path.exists("models/fine_tuned_model-v2.pt"):
            print("Fine-tuned model not found. Downloading Fine-tuned model... [Via OneDrive (Public)]")
            fine_tune_model_dl()
            try:
                if args.use_finetune == True:
                    whisper.load_model("models/fine_tuned_model-v2.pt", device=device, download_root="models")
                    print("Fine-tuned model loaded into memory.")
                    if device.type == "cuda":
                        max_split_size_mb = 128
            except Exception as e:
                print("Failed to load fine-tuned model. Results may be inaccurate. If you experience issues, please delete the fine-tuned model from the models folder and restart the program. If you still experience issues, please open an issue on GitHub.")
                red_text = Fore.RED + Back.BLACK
                print(f"{red_text}Error: {e}{reset_text}")
                pass
        else:
            try:
                if args.use_finetune == True:
                    whisper.load_model("models/fine_tuned_model-v2.pt", device=device, download_root="models")
                    print("Fine-tuned model loaded into memory.")
            except Exception as e:
                print("Failed to load fine-tuned model. Results may be inaccurate. If you experience issues, please delete the fine-tuned model from the models folder and restart the program. If you still experience issues, please open an issue on GitHub.")
                red_text = Fore.RED + Back.BLACK
                print(f"{red_text}Error: {e}{reset_text}")
                pass

    if args.ramforce:
        print("Hardmodel parameter detected. Setting ram flag to hardmodel parameter.")
        args.ram = hardmodel


    model = parser_args.set_model_by_ram(args.ram, args.language)
    print(f"Loading model {model}...")

    audio_model = whisper.load_model(model, device=device, download_root="models")

    record_timeout = args.record_timeout
    phrase_timeout = args.phrase_timeout

    if not os.path.exists("temp"):
        os.makedirs("temp")
    temp_dir = "temp"
    temp_file = NamedTemporaryFile(dir=temp_dir, delete=True, suffix=".ts", prefix="rec_").name
    transcription = ['']
        
    if args.discord_webhook:
        webhook_url = args.discord_webhook
        print(f"Sending console output to Discord webhook that was set in parameters.")

    recorder.listen_in_background(source, record_callback, phrase_time_limit=record_timeout)
    
    print("Model loaded.\n")
    print(f"Using {model} model.")
    if args.non_english:
        print("Using the multi-lingual model.")

    if device.type == "cuda":
        if "AMD" in torch.cuda.get_device_name(torch.cuda.current_device()):
            print("WARNING: You are using an AMD GPU with CUDA. This may not work properly. If you experience issues, try using the CPU instead.")

    english_counter = 0
    language_counters = {}
    last_detected_language = None 

    if args.discord_webhook:
        if args.translate:
            send_to_discord_webhook(webhook_url, f"Transcription started. Translation enabled.\nUsing the {args.ram} ram model.")
        else:
            send_to_discord_webhook(webhook_url, f"Transcription started. Translation disabled.\nUsing the {args.ram} ram model.")
        sleep(0.25)

    if args.auto_language_lock:
        print("Auto language lock enabled. Will auto lock after 5 consecutive detections of the same language.")
        if args.discord_webhook:
            send_to_discord_webhook(webhook_url, "Auto language lock enabled. Will auto lock after 5 consecutive detections of the same language.")

    print("Awaiting audio stream...")

    while True:
        try:
            now = datetime.utcnow()
            if not data_queue.empty():
                if args.no_log == False:
                    print("\nAudio stream detected...")
                phrase_complete = False
                if phrase_time and now - phrase_time > timedelta(seconds=phrase_timeout):
                    last_sample = bytes()
                    phrase_complete = True
                phrase_time = now

                while not data_queue.empty():
                    data = data_queue.get()
                    last_sample += data

                audio_data = sr.AudioData(last_sample, source.SAMPLE_RATE, source.SAMPLE_WIDTH)
                wav_data = io.BytesIO(audio_data.get_wav_data())

                with open(temp_file, 'w+b') as f:
                    f.write(wav_data.read())

                audio = whisper.load_audio(temp_file)
                audio = whisper.pad_or_trim(audio)
                mel = whisper.log_mel_spectrogram(audio).to(device)

                if ".en" in model:
                    detected_language = "English"
                else:
                    _, language_probs = audio_model.detect_language(mel)
                    detected_language = max(language_probs, key=language_probs.get)

                if args.language:
                    detected_language = args.language
                    if args.auto_language_lock:
                        if args.no_log == False:
                            print(f"Language locked to {detected_language}")
                    else:
                        if args.no_log == False:
                            print(f"Language set by argument: {detected_language}")
                else:
                    if ".en" in model:
                        detected_language = "English"
                        if args.no_log == False:
                            print(f"Language set by model: {detected_language}")
                    else:
                        if args.auto_language_lock:
                            if last_detected_language == detected_language:
                                english_counter += 1
                                if english_counter >= 5:
                                    if args.no_log == False:
                                        print(f"Language locked to {detected_language}")
                                    args.language = detected_language
                            else:
                                english_counter = 0
                                last_detected_language = detected_language
                        try:
                            confidence = language_probs[detected_language] * 100
                            confidence_color = Fore.GREEN if confidence > 75 else (Fore.YELLOW if confidence > 50 else Fore.RED)
                            set_window_title(detected_language, confidence)
                            if args.discord_webhook:
                                if args.no_log == False:
                                    print(f"Detected language: {detected_language} {confidence_color}({confidence:.2f}% Accuracy){Style.RESET_ALL}")
                        except:
                            pass
            

                if args.transcribe:
                    if args.no_log == False:
                        print("Transcribing...")
                
                if device == "cuda":
                    result = audio_model.transcribe(temp_file, fp16=torch.cuda.is_available(), language=detected_language)
                else:
                    result = audio_model.transcribe(temp_file)

                if args.no_log == False:
                    print(f"Detected Speech: {result['text']}")
                
                if result['text'] == "":
                    if args.retry:
                        if args.no_log == False:
                            print("Transcription failed, trying again...")
                        send_to_discord_webhook(webhook_url, "Transcription failed, trying again...")
                        if device == "cuda":
                            result = audio_model.transcribe(temp_file, fp16=torch.cuda.is_available(), language=detected_language)
                        else:
                            result = audio_model.transcribe(temp_file)
                        if args.no_log == False:
                            print(f"Detected Speech: {result['text']}")
                    else:
                        if args.no_log == False:
                            print("Transcription failed, skipping...")
                if args.discord_webhook:
                    send_to_discord_webhook(webhook_url, f"Detected Speech: {result['text']}")
                text = result['text'].strip()
                
                if args.translate:
                    if detected_language != 'en':
                        if args.no_log == False:
                            print("Translating...")
                        if device == "cuda":
                            translated_result = audio_model.transcribe(temp_file, fp16=torch.cuda.is_available(), task="translate", language=detected_language)
                        else:
                            translated_result = audio_model.transcribe(temp_file, task="translate", language=detected_language)
                        translated_text = translated_result['text'].strip()
                        if translated_text == "":
                            if args.retry:
                                if args.no_log == False:
                                    print("Translation failed, trying again...")
                                send_to_discord_webhook(webhook_url, "Translation failed, trying again...")
                                if device == "cuda":
                                    translated_result = audio_model.transcribe(temp_file, fp16=torch.cuda.is_available(), task="translate", language=detected_language)
                                else:
                                    translated_result = audio_model.transcribe(temp_file, task="translate", language=detected_language)
                            translated_text = translated_result['text'].strip()
                        if args.discord_webhook:
                            if translated_text == "":
                                send_to_discord_webhook(webhook_url, f"Translation failed")
                            else:
                                send_to_discord_webhook(webhook_url, f"Translated Speech: {translated_text}")

                    else:
                        translated_text = ""
                        if args.discord_webhook:
                            send_to_discord_webhook(webhook_url, "Translation failed")
            

                if args.transcribe:
                    if args.no_log == False:
                        print(f"Transcribing to {target_language}...")
                    if device == "cuda":
                        transcribed_result = audio_model.transcribe(temp_file, fp16=torch.cuda.is_available(), task="transcribe", language=target_language)
                    else:
                        transcribed_result = audio_model.transcribe(temp_file, task="transcribe", language=target_language)
                    transcribed_text = transcribed_result['text'].strip()
                    if transcribed_text == "":
                        if args.retry:
                            if args.no_log == False:
                                print("transcribe failed, trying again...")
                            send_to_discord_webhook(webhook_url, "transcribe failed, trying again...")
                            if device == "cuda":
                                transcribed_result = audio_model.transcribe(temp_file, fp16=torch.cuda.is_available(), task="transcribe", language=target_language)
                            else:
                                transcribed_result = audio_model.transcribe(temp_file, task="transcribe", language=target_language)
                        transcribed_text = transcribed_result['text'].strip()
                    if args.discord_webhook:
                        if transcribed_text == "":
                            send_to_discord_webhook(webhook_url, f"Translation failed")
                        else:
                            send_to_discord_webhook(webhook_url, f"transcribed Speech: {transcribed_text}")

                else:
                    transcribed_text = ""
                    if args.discord_webhook:
                        send_to_discord_webhook(webhook_url, "transcribe failed")
                
                if args.discord_webhook:
                    message = "----------------"
                    send_to_discord_webhook(webhook_url, message)
                    


                if phrase_complete:
                    transcription.append((text, translated_text if args.translate else None, transcribed_text if args.transcribe else None, detected_language))
                else:
                    transcription[-1] = (text, translated_text if args.translate else None, transcribed_text if args.transcribe else None, detected_language)

                os.system('cls' if os.name=='nt' else 'clear')

                if not args.no_log:
                    for original_text, translated_text, transcribed_text, detected_language in transcription:
                        if not original_text:
                            continue
                        print("=" * shutil.get_terminal_size().columns)
                        print(f"{' ' * int((shutil.get_terminal_size().columns - 15) / 2)} What was Heard -> {detected_language} {' ' * int((shutil.get_terminal_size().columns - 15) / 2)}")
                        print(f"{original_text}")

                    if args.translate and translated_text:
                        print(f"{'-' * int((shutil.get_terminal_size().columns - 15) / 2)} EN Translation {'-' * int((shutil.get_terminal_size().columns - 15) / 2)}")
                        print(f"{translated_text}\n")

                    if args.transcribe and transcribed_text:
                        print(f"{'-' * int((shutil.get_terminal_size().columns - 15) / 2)} {detected_language} -> {target_language} {'-' * int((shutil.get_terminal_size().columns - 15) / 2)}")
                        print(f"{transcribed_text}\n")

                else:
                    for original_text, translated_text, transcribed_text, detected_language in transcription:
                        if not original_text:
                            continue
                        if args.translate and translated_text:
                            print(f"{translated_text}")
                        if args.transcribe and transcribed_text:
                            print(f"{transcribed_text}")

                print('', end='', flush=True)


                if args.auto_model_swap:
                    if last_detected_language != detected_language:
                        last_detected_language = detected_language
                        language_counters[detected_language] = 1
                    else:
                        language_counters[detected_language] += 1

                    if language_counters[detected_language] == 5:
                        if detected_language == 'en' and model != 'base':
                            print("Detected English 5 times in a row, changing model to base.")
                            model = 'base'
                            audio_model = whisper.load_model(model, device=device)
                            print("Model was changed to base since English was detected 5 times in a row.")
                        elif detected_language != 'en' and model != 'large':
                            print(f"Detected {detected_language} 5 times in a row, changing model to large.")
                            model = 'large'
                            audio_model = whisper.load_model(model, device=device)
                            print(f"Model was changed to large since {detected_language} was detected 5 times in a row.")
        except Exception as e:
            if not isinstance(e, KeyboardInterrupt):
                print(e)
                if os.path.isfile('error_report.txt'):
                    error_report_file = open('error_report.txt', 'a')
                else:
                    error_report_file = open('error_report.txt', 'w')
                error_report_file.write(str(e))
                error_report_file.close()
            pass

        except KeyboardInterrupt:
            print("Exiting...")
            if args.discord_webhook:
                send_to_discord_webhook(webhook_url, "Service has stopped.")
            break

    if not os.path.isdir('out'):
        os.mkdir('out')
    
    transcript = os.path.join(os.getcwd(), 'out', 'transcription.txt')
    if os.path.isfile(transcript):
        transcript = os.path.join(os.getcwd(), 'out', 'transcription_' + str(len(os.listdir('out'))) + '.txt')
    transcription_file = open(transcript, 'w',  encoding='utf-8')

    for original_text, translated_text, transcribed_text, detected_language in transcription:
        transcription_file.write(f"-=-=-=-=-=-=-=-\nOriginal ({detected_language}): {original_text}\n")
        if translated_text:
            transcription_file.write(f"Translation: {translated_text}\n")
        if transcribed_text:
            transcription_file.write(f"Transcription: {transcribed_text}\n")
    transcription_file.close()
    print(f"Transcription was saved to {transcript}")
    

if __name__ == "__main__":
    main()