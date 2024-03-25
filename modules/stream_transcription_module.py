# stream_transcription_module.py
from modules.imports import *

# Global shutdown flag
shutdown_flag = False
args = parser_args.parse_arguments()

def load_cookies_from_file(cookie_file_path):
    cookie_jar = http.cookiejar.MozillaCookieJar()
    cookie_jar.load(cookie_file_path, ignore_discard=True, ignore_expires=True)
    return cookie_jar

def start_stream_transcription(task_id, hls_url, model_name, temp_dir, segments_max, target_language, stream_language, tasktranslate_task, tasktranscribe_task, webhook_url, cookie_file_path=None):

    global shutdown_flag
    audio_queue = queue.Queue()

    # Load cookies if a cookie file path is provided
    cookies = None
    if cookie_file_path:
        cookies = load_cookies_from_file(cookie_file_path)

    def download_segment(segment_url, output_path, max_retries=3, retry_delay=5):
        retry_count = 0
        while retry_count < max_retries:
            try:
                response = requests.get(segment_url, stream=True, cookies=cookies) if cookies else requests.get(
                    segment_url, stream=True)
                if response.status_code == 200:
                    with open(output_path, 'wb') as file:
                        for chunk in response.iter_content(chunk_size=16000):
                            file.write(chunk)
                    return True
                else:
                    print(f"Failed to download segment, status code: {response.status_code}")
                    break
            except requests.exceptions.RequestException as e:
                print(f"Network error: {e}, retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
                retry_count += 1
            except Exception as e:
                print(f"Unexpected error downloading segment: {e}")
                break
        # Clean up partial file if exists
        if os.path.exists(output_path):
            os.remove(output_path)
        return False

    def load_m3u8_with_retry(hls_url, retry_delay=5):
        while not shutdown_flag:
            try:
                m3u8_obj = m3u8.load(hls_url)
                return m3u8_obj
            except (
            http.client.RemoteDisconnected, http.client.IncompleteRead, requests.exceptions.RequestException) as e:
                print(f"Error loading m3u8 file: {e}. Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            except Exception as e:
                print(f"Unexpected error loading m3u8 file: {e}")
                time.sleep(retry_delay)
        return None

    def generate_segment_filename(url, counter, task_id):
        url_hash = hashlib.md5(url.encode()).hexdigest()
        return os.path.join(temp_dir, f"{task_id}_{counter:05d}_{url_hash}.ts")

    def combine_audio_segments(segment_paths, output_path):
        with open(output_path, 'wb') as outfile:
            for segment_path in segment_paths:
                if not os.path.exists(segment_path):
                    print(f"Warning: File {segment_path} does not exist, skipping.")
                    continue
                try:
                    with open(segment_path, 'rb') as infile:
                        outfile.write(infile.read())
                    os.remove(segment_path)
                except Exception as e:
                    print(f"Error combining audio segments: {e}")

    def translate_audio(file_path, model):
        try:
            result = model.transcribe(file_path, task="translate", language=stream_language)
            return result["text"]
        except RuntimeError as e:
            print(f"Error transcribing audio: {e}")
            return ""

    def transcribe_audio(file_path, model, language):
        try:
            result = model.transcribe(file_path, language=language)
            return result["text"]
        except RuntimeError as e:
            print(f"Error transcribing audio: {e}")
            return ""

    def detect_language(file_path, model, device=args.device):
        try:
            audio = whisper.load_audio(file_path)
            audio = whisper.pad_or_trim(audio)
            if args.ram == "12gb":
                mel = whisper.log_mel_spectrogram(audio, n_mels=128).to(device)
            else:
                mel = whisper.log_mel_spectrogram(audio, n_mels=80).to(device)
            _, language_probs = model.detect_language(mel)
            detected_language = max(language_probs, key=language_probs.get)
            return detected_language
        except RuntimeError as e:
            print(f"Error detecting language: {e}")
            detected_language = "n/a"
            return detected_language

    def process_audio_queue(model):
        while True:
            file_path = audio_queue.get()
            if file_path is None or not os.path.exists(file_path):
                if file_path:
                    print(f"Warning: File {file_path} does not exist, skipping.")
                continue

            transcription = None
            translation = None
            if args.stream_original_text:
                if args.stream_language:
                    detected_language = stream_language
                    #print(f"Language Set By Args: {detected_language}")
                else:
                    #print("Testing for Language")
                    detected_language = detect_language(file_path, model)
                    #print(f"Language is: {detected_language}")
                transcription = transcribe_audio(file_path, model, language=detected_language)
                print(f"{'-' * 50} {detected_language} Original {'-' * 50}")
                print(transcription)
                if args.portnumber:
                    new_header = f"({detected_language}) {transcription}"
                    api_backend.update_header(new_header)

            if tasktranslate_task:
                translation = translate_audio(file_path, model)
                if translation:
                    print(f"{'-' * 50} Stream EN Translation {'-' * 50}")
                    print(translation)
                    if webhook_url:
                        send_to_discord_webhook(webhook_url, f"Stream EN Translation:\n{translation}\n")
                    if args.portnumber:
                        new_header = f"{translation}"
                        api_backend.update_translated_header(new_header)

            if tasktranscribe_task:
                transcription = transcribe_audio(file_path, model, language=target_language)
                if transcription:
                    print(f"{'-' * 50} Stream {target_language} Transcription {'-' * 50}")
                    print(transcription)
                    if webhook_url:
                        send_to_discord_webhook(webhook_url, f"Stream {target_language} Transcription:\n{transcription}\n")
                    if args.portnumber:
                        new_header = f"{transcription}"
                        api_backend.update_transcribed_header(new_header)

            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
            except Exception as e:
                print(f"Error removing file {file_path}: {e}")

    # Start processing thread
    processing_thread = threading.Thread(target=process_audio_queue, args=(model_name,))
    processing_thread.daemon = True
    processing_thread.start()

    # Main loop for downloading and combining segments
    try:
        downloaded_segments = set()
        counter = 0
        accumulated_segments = []

        while not shutdown_flag:
            m3u8_obj = load_m3u8_with_retry(hls_url)
            if not m3u8_obj:
                print("Failed to load m3u8 after retries, stopping.")
                break

            for segment in m3u8_obj.segments:
                if segment.uri not in downloaded_segments:
                    segment_path = generate_segment_filename(segment.uri, counter, task_id)
                    counter += 1
                    if download_segment(segment.absolute_uri, segment_path):
                        downloaded_segments.add(segment.uri)
                        accumulated_segments.append(segment_path)

                        if len(accumulated_segments) >= segments_max:
                            combined_path = os.path.join(temp_dir, f"{task_id}_combined_{counter}.ts")
                            combine_audio_segments(accumulated_segments, combined_path)
                            audio_queue.put(combined_path)
                            accumulated_segments = []

    except KeyboardInterrupt:
        shutdown_flag = True  # Signal to shut down

    # Cleanup
    for file in os.listdir(temp_dir):
        os.remove(os.path.join(temp_dir, file))
    audio_queue.put(None)
    processing_thread.join()

def stop_transcription():
    global shutdown_flag
    shutdown_flag = True

print("Stream Transcription Module Loaded")
