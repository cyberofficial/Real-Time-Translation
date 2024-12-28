try:
    print("Loading Primary Imports")
    from modules.imports import *
    print("\n\n")
except Exception as e:
    print("Error Loading Primary Imports")
    print("Check the Modules folder for the imports.py file and make sure it is not missing or corrupted.")
    print(e)
    sys.exit(1)

init()

try:
    cuda_available = torch.cuda.is_available()
except:
    cuda_available = False

# Code is semi documented, but if you have any questions, feel free to ask in the Discussions tab.

def main():

    global translated_text, target_language, language_probs, webhook_url, required_vram, original_text, phrase_timeout
    args = parser_args.parse_arguments()

    def load_blacklist(filename):
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

    if args.ignorelist:
        print(f"Loaded word filtering list from: {args.ignorelist}")
        blacklist = load_blacklist(args.ignorelist)

    else:
        blacklist = []

    # if blacklist.txt was found say loaded
    if len(blacklist) > 0:
        print(f"Loaded blacklist: {blacklist}")

    # Check for Stream or Microphone is no present then exit
    if args.stream == None and args.microphone_enabled == None:
        if args.makecaptions:
            # skip if makecaptions is set
            pass
        else:
            print("No audio source was set. Please set an audio source.")
            reset_text = Style.RESET_ALL
            input(f"Press {Fore.YELLOW}[enter]{reset_text} to exit.")
            sys.exit("Exiting...")




    # If stream and microphone is set then exit saying you can only use one input source
    if args.stream != None and args.microphone_enabled != None:
        print("You can only use one input source. Please only set one input source.")
        reset_text = Style.RESET_ALL
        input(f"Press {Fore.YELLOW}[enter]{reset_text} to exit.")
        sys.exit("Exiting...")

    if args.stream_transcribe and args.stream_target_language == None:
        print("Stream Transcribe is set but no stream target language is set. Please set a stream target language.")
        sys.exit("Exiting...")


    # if args.updatebranch is set as disable then skip
    if args.updatebranch != "disable":
        print("\nChecking for updates...")
        try:
            check_for_updates(args.updatebranch)
        except Exception as e:
            print("Error checking for updates.")
            print("Error: " + str(e))
            print("Continuing with script...\n\n")

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
        print("No arguments provided. Please run the script with the --help flag to see a list of available arguments.")
        sys.exit(1)

    if args.about:
        from modules.about import contributors
        from modules.version_checker import ScriptCreator, GitHubRepo
        contributors(ScriptCreator, GitHubRepo)

    model = ""

    hardmodel = None

    if args.ramforce:
        hardmodel = args.ram

    phrase_time = None
    last_sample = bytes()
    data_queue = Queue()
    recorder = sr.Recognizer()
    recorder.energy_threshold = args.energy_threshold
    recorder.dynamic_energy_threshold = False
    reset_text = Style.RESET_ALL


    def mic_calibration():
        print("Starting mic calibration...")
        with sr.Microphone() as source:
            recorder.adjust_for_ambient_noise(source, duration=args.mic_calibration_time)
            print(f"Calibration complete. The microphone is set to: {Fore.YELLOW}" + str(recorder.energy_threshold) + f"{reset_text}")

    if args.list_microphones:
        print("Available microphone devices are: ")
        mic_table = PrettyTable()
        mic_table.field_names = ["Index", "Microphone Name"]

        for index, name in enumerate(sr.Microphone.list_microphone_names()):
            if is_input_device(index):
                mic_table.add_row([index, name])

        print(mic_table)
        input(f"Press {Fore.YELLOW}[enter]{reset_text} to exit.")
        sys.exit(0)

    if args.microphone_enabled:
        if args.mic_calibration_time:
            print("Mic calibration flag detected.\n")
            print(f"Press {Fore.YELLOW}[enter]{reset_text} when ready to start mic calibration.\nMake sure there is no one speaking during this time.")
            if args.mic_calibration_time == 0:
                args.mic_calibration_time = 5
                mic_calibration()
            else:
                print("Waiting for user input...")
                input()
                mic_calibration()
                print(f"If you are happy with this setting press {Fore.YELLOW}[enter]{reset_text} or type {Fore.YELLOW}[r]{reset_text} then {Fore.YELLOW}[enter]{reset_text} to recalibrate.\n")
                while True:
                    user_input = input("r/enter: ")
                    if user_input == "r":
                        mic_calibration()
                        print(f"If you are happy with this setting press {Fore.YELLOW}[enter]{reset_text} or type {Fore.YELLOW}[r]{reset_text} then {Fore.YELLOW}[enter]{reset_text} to recalibrate.\n")
                    else:
                        break

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

    if args.microphone_enabled:
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

    if args.portnumber:
        print("Port number was set, so spinning up a web server...")
        api_backend.flask_server(operation="start", portnumber=args.portnumber)

    try:
        if args.microphone_enabled:
            source, mic_name = get_microphone_source(args)
    except ValueError as e:
        print(
            "It may look like the microphone is not working, make sure your microphone is plugged in and working, or make sure your privacy settings allow microphone access, or make sure you have a microphone selected, or make sure you have a softwaare microphone selected: ie: Voicemeeter, VB-Cable, etc.")
        print("Error Message:\n" + str(e))
        pass

    if args.microphone_enabled:
        with source as s:
            try:
                recorder.adjust_for_ambient_noise(s)
                print(f"Microphone set to: {mic_name}")
            except AssertionError as e:
                print("It may look like the microphone is not working, make sure your microphone is plugged in and working, or make sure your privacy settings allow microphone access, or make sure you have a microphone selected, or make sure you have a softwaare microphone selected: ie: Voicemeeter, VB-Cable, etc.")
                print("Error Message:\n" + str(e))
                pass

    if args.language == "en" or args.language == "English":
        model += ".en"
        if model == "large" or model == "large.en":
            model = "large"

    if not os.path.exists(f"{args.model_dir}"):
        print("Creating models folder...")
        os.makedirs(f"{args.model_dir}")

    if device.type == "cuda":
        cuda_vram = torch.cuda.get_device_properties(torch.cuda.current_device()).total_memory / 1024 / 1024
        overhead_buffer = 200

        ram_options = [("12gb-v2", 12000), ("6gb", 6144), ("4gb", 4096), ("2gb", 2048), ("1gb", 1024)]

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

    # Obsolete -- Will Adjust in future
    #if args.ram == "1gb" or args.ram == "2gb" or args.ram == "4gb":
    #    red_text = Style.BRIGHT + Fore.RED
    #    if not os.path.exists(f"{args.model_dir}/fine_tuned_model_compressed_v2.pt"):
    #        print("Warning - Since you have chosen a low amount of RAM, the fine-tuned model will be downloaded in a compressed format.\nThis will result in a some what faster startup time and a slower inference time, but will also result in slight reduction in accuracy.")
    #        print("Compressed Fine-tuned model not found. Downloading Compressed fine-tuned model... [Via OneDrive (Public)]")
    #        #fine_tune_model_dl_compressed(args.model_dir)
    #        try:
    #            if args.use_finetune == True:
    #                whisper.load_model(f"{args.model_dir}/fine_tuned_model_compressed_v2.pt", device=device, download_root=f"{args.model_dir}")
    #                print("Fine-tuned model loaded into memory.")
    #                if device.type == "cuda":
    #                    max_split_size_mb = 128
    #        except Exception as e:
    #            red_text = Fore.RED + Back.BLACK
    #            print("Failed to load fine-tuned model. Results may be inaccurate. If you experience issues, please delete the fine-tuned model from the models folder and restart the program. If you still experience issues, please open an issue on GitHub.")
    #            print(f"{red_text}Sometimes Microsoft Onedrive will block the download, please download manually from here https://onedrive.live.com/download?cid=22FB8D582DCFA12B&resid=22FB8D582DCFA12B%21456433&authkey=AOTrQ949dOFhdxQ")
    #            print(f"{red_text}Error: {e}{reset_text}")
    #            print("Press Enter to continue...")
    #            input()
    #            pass
    #    else:
    #        try:
    #            if args.use_finetune == True:
    #                whisper.load_model(f"{args.model_dir}/fine_tuned_model_compressed_v2.pt", device=device, download_root=f"{args.model_dir}")
    #                print("Fine-tuned model loaded into memory.")
    #                if device.type == "cuda":
    #                    max_split_size_mb = 128
    #        except Exception as e:
    #            red_text = Fore.RED + Back.BLACK
    #            print("Failed to load fine-tuned model. Results may be inaccurate. If you experience issues, please delete the fine-tuned model from the models folder and restart the program. If you still experience issues, please open an issue on GitHub.")
    #            print(
    #                f"{red_text}Sometimes Microsoft Onedrive will block the download, please download manually from here https://onedrive.live.com/download?cid=22FB8D582DCFA12B&resid=22FB8D582DCFA12B%21456433&authkey=AOTrQ949dOFhdxQ")
    #            print(f"{red_text}Error: {e}{reset_text}")
    #            print("Press Enter to continue...")
    #            input()
    #            pass
    #else:
    #    if not os.path.exists(f"{args.model_dir}/fine_tuned_model-v2.pt"):
    #        print("Fine-tuned model not found. Downloading Fine-tuned model... [Via OneDrive (Public)]")
    #        fine_tune_model_dl(args.model_dir)
    #        try:
    #            if args.use_finetune == True:
    #                whisper.load_model(f"{args.model_dir}/fine_tuned_model-v2.pt", device=device, download_root=f"{args.model_dir}")
    #                print("Fine-tuned model loaded into memory.")
    #                if device.type == "cuda":
    #                    max_split_size_mb = 128
    #        except Exception as e:
    #            red_text = Fore.RED + Back.BLACK
    #            print("Failed to load fine-tuned model. Results may be inaccurate. If you experience issues, please delete the fine-tuned model from the models folder and restart the program. If you still experience issues, please open an issue on GitHub.")
    #            print(
    #                f"{red_text}Sometimes Microsoft Onedrive will block the download, please download manually from here https://onedrive.live.com/download?cid=22FB8D582DCFA12B&resid=22FB8D582DCFA12B%21456432&authkey=AIRKZih0go6iUTs")
    #            print(f"{red_text}Error: {e}{reset_text}")
    #            print("Press Enter to continue...")
    #            input()
    #            pass
    #    else:
    #        try:
    #            if args.use_finetune == True:
    #                whisper.load_model(f"{args.model_dir}/fine_tuned_model-v2.pt", device=device, download_root=f"{args.model_dir}")
    #                print("Fine-tuned model loaded into memory.")
    #        except Exception as e:
    #            red_text = Fore.RED + Back.BLACK
    #            print("Failed to load fine-tuned model. Results may be inaccurate. If you experience issues, please delete the fine-tuned model from the models folder and restart the program. If you still experience issues, please open an issue on GitHub.")
    #            print(
    #                f"{red_text}Sometimes Microsoft Onedrive will block the download, please download manually from here https://onedrive.live.com/download?cid=22FB8D582DCFA12B&resid=22FB8D582DCFA12B%21456432&authkey=AIRKZih0go6iUTs")
    #            print(f"{red_text}Error: {e}{reset_text}")
    #            print("Press Enter to continue...")
    #            input()
    #            pass

    if args.ramforce:
        print("Hardmodel parameter detected. Setting ram flag to hardmodel parameter.")
        args.ram = hardmodel

    if args.target_language:
        model = parser_args.set_model_by_ram(args.ram, args.language)
    else:
        model = parser_args.set_model_by_ram(args.ram, args.language)
    print(f"Loading model {model}...\n")

    # remove .en from model if target_language is not set to English
    if not args.makecaptions:
        if args.target_language != "en" or args.target_language != "English":
            model = model.replace(".en", "")
            #print(f"Loading model {model} instead since target language is not English...")
        audio_model = whisper.load_model(model, device=device, download_root=f"{args.model_dir}")

    if args.microphone_enabled:
        record_timeout = args.record_timeout
        phrase_timeout = args.phrase_timeout

    if not os.path.exists("temp"):
        os.makedirs("temp")
    temp_dir = "temp"
    if args.keep_temp:
        keep = True
        print("Keeping temporary files, warning this will take up a lot of space over time.")
    else:
        keep = False
        print("Keeping temporary files disabled.")
    if args.microphone_enabled:
        temp_file = NamedTemporaryFile(dir=temp_dir, delete=keep, suffix=".ts", prefix="rec_").name
    transcription = ['']

    if args.discord_webhook:
        webhook_url = args.discord_webhook
        print(f"Sending console output to Discord webhook that was set in parameters.")

    if args.microphone_enabled:
        recorder.listen_in_background(source, record_callback, phrase_time_limit=record_timeout)

    print("Model loaded.\n")
    print(f"Using {model} model.")

    if device.type == "cuda":
        if "AMD" in torch.cuda.get_device_name(torch.cuda.current_device()):
            print("WARNING: You are using an AMD GPU with CUDA. This may not work properly. If you experience issues, try using the CPU instead.")

    english_counter = 0
    language_counters = {}
    last_detected_language = None

    if args.makecaptions:
        # from modules.sub_gen import run_sub_gen
        if args.file_output_name == None:
            args.file_output_name = "filename"
        run_sub_gen(args.file_input, args.file_output_name, args.file_output)
        print("Press enter to exit...")
        input()
        sys.exit("Exiting...")

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

    if args.stream:
        print("Stream mode enabled.")
        print(f"You have chosen to use the stream {args.stream}.")

        # Define the temp directory and model name
        temp_dir = os.path.join(os.getcwd(), "./temp")
        os.makedirs(temp_dir, exist_ok=True)
        model_name = audio_model  # or any other model you want to use

        stream_language = args.stream_language
        if args.stream_target_language:
            target_language = args.stream_target_language
        else:
            target_language = "en"
        if args.stream_translate:
            tasktranslate_task = True
        else:
            tasktranslate_task = False
        if args.stream_transcribe:
            tasktranscribe_task = True
        else:
            tasktranscribe_task = False

        if args.discord_webhook:
            if args.stream_translate:
                send_to_discord_webhook(webhook_url, f"Stream Transcription started. Translation enabled.\nUsing the {args.ram} ram model.")
            if args.stream_transcribe:
                send_to_discord_webhook(webhook_url, f"Stream Transcription started. Transcription enabled.\nUsing the {args.ram} ram model.")
        else:
            webhook_url = None

        cookie_file_path = None
        # Get HLS URL using yt-dlp
        hls_url = subprocess.check_output(["yt-dlp", args.stream, "-g"]).decode("utf-8").strip()

        if args.cookies:
            # f"cookies\\{args.cookies}.txt"
            cookie_file_path = f"cookies\\{args.cookies}.txt"
            # update hls_url with cookies if cookies are set
            hls_url = subprocess.check_output(["yt-dlp", args.stream, "-g", "--cookies", cookie_file_path]).decode("utf-8").strip()


        print(f"Found the Stream URL:\n{hls_url}")

        # generated a random 6 digit number for the task id
        import random
        task_id = random.randint(100000, 999999)

        if args.remote_hls_password_id:
            streamkey = True
        else:
            streamkey = False


        # Start stream transcription
        segments_max = args.stream_chunks if hasattr(args, 'stream_chunks') else 1
        # start start_stream_transcription(hls_url, model_name, temp_dir, segments_max) in a new thread
        stream_thread = threading.Thread(target=start_stream_transcription,
                                         args=(task_id, hls_url, model_name, temp_dir, segments_max, target_language, stream_language, tasktranslate_task, tasktranscribe_task, webhook_url, cookie_file_path, streamkey))
        stream_thread.start()

    if args.microphone_enabled:
        print("Awaiting audio stream from microphone...")
    else:
        print("Microphone disabled. Awaiting audio stream from stream...")

   #if args.portnumber:
   #    new_header = f"({detected_language}) {original_text}"
   #    api_backend.update_header(new_header)
   #    new_header = f"{translated_text}"
   #    api_backend.update_translated_header(new_header)
   #    new_header = f"{transcribed_text}"
   #    api_backend.update_transcribed_header(new_header)


    global detected_language
    global original_text
    global transcribed_text
    global text

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
                if args.ram == "12gb-v3":
                    mel = whisper.log_mel_spectrogram(audio, n_mels=128).to(device)
                else:
                    mel = whisper.log_mel_spectrogram(audio, n_mels=80).to(device)

                if ".en" in model:
                    detected_language = "English"
                else:
                    if args.stream_language:
                        print(f"Language Set: {args.stream_language}\n")
                        detected_language = args.stream_language
                    else:
                        if args.no_log == False:
                            print(f"Detecting Language\n")
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
                    result = audio_model.transcribe(temp_file, fp16=args.fp16, language=detected_language, condition_on_previous_text=args.condition_on_previous_text)
                else:
                    result = audio_model.transcribe(temp_file, language=detected_language, condition_on_previous_text=args.condition_on_previous_text)

                if args.no_log == False:
                    print(f"Detected Speech: {result['text']}")

                if result['text'] == "":
                    if args.retry:
                        if args.no_log == False:
                            print("Transcription failed, trying again...")
                        send_to_discord_webhook(webhook_url, "Transcription failed, trying again...")
                        if device == "cuda":
                            result = audio_model.transcribe(temp_file, fp16=args.fp16, language=detected_language, condition_on_previous_text=args.condition_on_previous_text)
                        else:
                            result = audio_model.transcribe(temp_file, language=detected_language, condition_on_previous_text=args.condition_on_previous_text)
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
                            translated_result = audio_model.transcribe(temp_file, fp16=args.fp16, task="translate", language=detected_language, condition_on_previous_text=args.condition_on_previous_text)
                        else:
                            translated_result = audio_model.transcribe(temp_file, task="translate", language=detected_language, condition_on_previous_text=args.condition_on_previous_text)
                        translated_text = translated_result['text'].strip()
                        if translated_text == "":
                            if args.retry:
                                if args.no_log == False:
                                    print("Translation failed, trying again...")
                                send_to_discord_webhook(webhook_url, "Translation failed, trying again...")
                                if device == "cuda":
                                    translated_result = audio_model.transcribe(temp_file, fp16=args.fp16, task="translate", language=detected_language, condition_on_previous_text=args.condition_on_previous_text)
                                else:
                                    translated_result = audio_model.transcribe(temp_file, task="translate", language=detected_language, condition_on_previous_text=args.condition_on_previous_text)
                            translated_text = translated_result['text'].strip()
                        if args.discord_webhook:
                            if translated_text == "":
                                send_to_discord_webhook(webhook_url, f"Translation failed")
                            else:
                                send_to_discord_webhook(webhook_url, f"Translated Speech: {translated_text}")

                    else:
                        translated_text = ""
                        new_header = f"{translated_text}"
                        api_backend.update_translated_header(new_header)
                        if args.discord_webhook:
                            send_to_discord_webhook(webhook_url, "Translation failed")

                if args.transcribe:
                    if args.no_log == False:
                        print(f"Transcribing to {target_language}...")
                    if device == "cuda":
                        transcribed_result = audio_model.transcribe(temp_file, fp16=args.fp16, task="transcribe", language=target_language, condition_on_previous_text=args.condition_on_previous_text)
                    else:
                        transcribed_result = audio_model.transcribe(temp_file, task="transcribe", language=target_language, condition_on_previous_text=args.condition_on_previous_text)
                    transcribed_text = transcribed_result['text'].strip()
                    if transcribed_text == "":
                        if args.retry:
                            if args.no_log == False:
                                print("transcribe failed, trying again...")
                            send_to_discord_webhook(webhook_url, "transcribe failed, trying again...")
                            if device == "cuda":
                                transcribed_result = audio_model.transcribe(temp_file, fp16=args.fp16, task="transcribe", language=target_language, condition_on_previous_text=args.condition_on_previous_text)
                            else:
                                transcribed_result = audio_model.transcribe(temp_file, task="transcribe", language=target_language, condition_on_previous_text=args.condition_on_previous_text)
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

                if args.portnumber:
                    try:
                        # Filter original_text for the header
                        filtered_header_text = original_text.lower()
                        for phrase in blacklist:
                            filtered_header_text = re.sub(rf"\b{phrase.lower()}\b", "", filtered_header_text).strip()

                        #if filtered_header_text:
                            #new_header = f"({detected_language}) {filtered_header_text}"
                        new_header = f"{filtered_header_text}"
                        api_backend.update_header(new_header)
                    except:
                        pass
                    try:
                        # Filter translated_text for the header
                        filtered_translated_text = translated_text.lower()
                        for phrase in blacklist:
                            filtered_translated_text = re.sub(rf"\b{phrase.lower()}\b", "",
                                                              filtered_translated_text).strip()
                        #if filtered_translated_text:
                        new_header = f"{filtered_translated_text}"
                        api_backend.update_translated_header(new_header)
                    except:
                        pass
                    try:
                        # Filter transcribed_text for the header
                        filtered_transcribed_text = transcribed_text.lower()
                        for phrase in blacklist:
                            filtered_transcribed_text = re.sub(rf"\b{phrase.lower()}\b", "",
                                                               filtered_transcribed_text).strip()
                        #if filtered_transcribed_text:
                        new_header = f"{filtered_transcribed_text}"
                        api_backend.update_transcribed_header(new_header)
                    except:
                        pass


                #os.system('cls' if os.name=='nt' else 'clear')

                # Always fetch the latest transcription
                original_text, translated_text, transcribed_text, detected_language = transcription[-1]

                # Filter text based on blacklist using regex
                filtered_text = original_text.lower()
                for phrase in blacklist:
                    filtered_text = re.sub(rf"\b{phrase.lower()}\b", "", filtered_text).strip()

                if filtered_text:  # Only continue if there’s text left after filtering
                    # If logging is enabled
                    if not args.no_log:
                        print("=" * shutil.get_terminal_size().columns)
                        print(
                            f"{' ' * int((shutil.get_terminal_size().columns - 15) / 2)} What was Heard -> {detected_language} {' ' * int((shutil.get_terminal_size().columns - 15) / 2)}")
                        print(f"{filtered_text}")  # Display filtered text
                        new_header = filtered_text

                        if args.translate and translated_text:
                            # Filter and print translated text
                            filtered_translated_text = translated_text
                            for phrase in blacklist:
                                filtered_translated_text = re.sub(rf"\b{phrase.lower()}\b", "",
                                                                  filtered_translated_text).strip()

                            print(
                                f"{'-' * int((shutil.get_terminal_size().columns - 15) / 2)} EN Translation {'-' * int((shutil.get_terminal_size().columns - 15) / 2)}")
                            print(f"{filtered_translated_text}\n")

                        if args.transcribe and transcribed_text:
                            # Filter and print transcribed text
                            filtered_transcribed_text = transcribed_text
                            for phrase in blacklist:
                                filtered_transcribed_text = re.sub(rf"\b{phrase.lower()}\b", "",
                                                                   filtered_transcribed_text).strip()

                            print(
                                f"{'-' * int((shutil.get_terminal_size().columns - 15) / 2)} {detected_language} -> {target_language} {'-' * int((shutil.get_terminal_size().columns - 15) / 2)}")
                            print(f"{filtered_transcribed_text}\n")

                    # Update header regardless of no_log
                    new_header = filtered_text
                    if args.portnumber:
                        api_backend.update_header(new_header)

                    # Simple one-line format for no_log
                    if args.no_log:
                        print(f"[Input ({detected_language})]: {filtered_text}\n")

                        if args.transcribe and transcribed_text:
                            filtered_transcribed_text = transcribed_text
                            for phrase in blacklist:
                                filtered_transcribed_text = re.sub(rf"\b{phrase.lower()}\b", "",
                                                                   filtered_transcribed_text).strip()
                            print(
                                f"[Transcription ({detected_language} -> {target_language})]: {filtered_transcribed_text}\n")

                        if args.translate and translated_text:
                            filtered_translated_text = translated_text
                            for phrase in blacklist:
                                filtered_translated_text = re.sub(rf"\b{phrase.lower()}\b", "",
                                                                  filtered_translated_text).strip()
                            print(f"[Translation (EN)]: {filtered_translated_text}\n")

                print('', end='', flush=True)

            # sleep for half second
            sleep(0.5)
        
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
            # kill stream_thread
            if args.stream:
                stop_transcription()
                # clear temp folder of files that do not start with "rec_"
                try:
                    for file in os.listdir(temp_dir):
                        if not file.startswith("rec_"):
                            os.remove(os.path.join(temp_dir, file))
                except Exception as e:
                    pass


            if args.discord_webhook:
                send_to_discord_webhook(webhook_url, "**Service has stopped.**")
            # break

            if args.save_transcript:
                # if args.save_folder isn't set use "out" as the default
                if not args.output:
                    out = "out"
                else:
                    out = args.output
                if not os.path.isdir(out):
                    os.mkdir(out)

                transcript = os.path.join(os.getcwd(), out, 'transcription.txt')
                if os.path.isfile(transcript):
                    transcript = os.path.join(os.getcwd(), out, 'transcription_' + str(len(os.listdir(out))) + '.txt')
                transcription_file = open(transcript, 'w',  encoding='utf-8')

                for original_text, translated_text, transcribed_text, detected_language in transcription:
                    transcription_file.write(f"-=-=-=-=-=-=-=-\nOriginal ({detected_language}): {original_text}\n")
                    if translated_text:
                        transcription_file.write(f"Translation: {translated_text}\n")
                    if transcribed_text:
                        transcription_file.write(f"Transcription: {transcribed_text}\n")
                transcription_file.close()
                print(f"Transcription was saved to {transcript}")

            if args.portnumber:
                api_backend.kill_server()

            sys.exit(0)
            
if __name__ == "__main__":
    main()