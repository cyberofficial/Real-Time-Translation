"""
Stream Transcription Module

This module handles real-time transcription and translation of HLS audio streams.
It provides functionality to:
- Download and process HLS stream segments
- Transcribe audio in original language
- Translate audio to English
- Send transcriptions/translations to Discord webhook
- Support for authenticated streams via cookies or stream keys

The module uses a threaded approach to handle concurrent downloading and processing
of audio segments, with support for retry logic and error handling.
"""

import threading
import queue
import time
import requests
import hashlib
import os
import m3u8
import http.client
import http.cookiejar
import whisper
from modules import parser_args
from modules.discord import send_to_discord_webhook
from modules import api_backend

# Global shutdown flag
shutdown_flag = False
args = parser_args.parse_arguments()
kill = False

# Set debug to true
# args.debug = True

# Semaphore for limiting concurrent downloads (adjust as needed)
max_concurrent_downloads = 4
download_semaphore = threading.Semaphore(max_concurrent_downloads)

def load_cookies_from_file(cookie_file_path):
    """
    Load cookies from a Mozilla format cookies file.

    Args:
        cookie_file_path (str): Path to the cookie file in Mozilla format

    Returns:
        http.cookiejar.MozillaCookieJar: Loaded cookie jar object containing the cookies

    This function is used for authenticated streams that require cookies for access.
    The cookies are loaded with both discarded and expired cookies included.
    """
    cookie_jar = http.cookiejar.MozillaCookieJar()
    cookie_jar.load(cookie_file_path, ignore_discard=True, ignore_expires=True)
    return cookie_jar



def start_stream_transcription(
    task_id,
    hls_url,
    model_name,
    temp_dir,
    segments_max,
    target_language,
    stream_language,
    tasktranslate_task,
    tasktranscribe_task,
    webhook_url,
    cookie_file_path=None,
    streamkey=None,
):
    """
    Start transcription and translation of an HLS audio stream.

    Args:
        task_id (str): Unique identifier for this transcription task
        hls_url (str): URL of the HLS stream to process
        model_name (whisper.Whisper): Loaded Whisper model instance
        temp_dir (str): Directory path for temporary files
        segments_max (int): Maximum number of segments to process at once
        target_language (str): Target language code for transcription
        stream_language (str): Source language code of the stream
        tasktranslate_task (bool): Whether to translate to English
        tasktranscribe_task (bool): Whether to transcribe in target language
        webhook_url (str, optional): Discord webhook URL for sending results
        cookie_file_path (str, optional): Path to Mozilla format cookies file
        streamkey (str, optional): Authentication key for protected streams

    The function handles downloading stream segments, combining them into
    processable chunks, and running transcription/translation based on
    the specified tasks. It uses threading for concurrent processing and
    includes retry logic for robust operation.
    """

    if streamkey:
        keyid = args.remote_hls_password_id
        key = args.remote_hls_password
        params = {keyid: key}
    else:
        params = None

    global shutdown_flag
    audio_queue = queue.Queue()

    # Load cookies if a cookie file path is provided
    cookies = None
    if cookie_file_path:
        cookies = load_cookies_from_file(cookie_file_path)

    def download_segment(
        segment_url, output_path, max_retries=3, retry_delay=0.5, segment_delay=0
    ):
        """
        Download an HLS segment with retry logic and error handling.

        Args:
            segment_url (str): URL of the segment to download
            output_path (str): Path where the downloaded segment will be saved
            max_retries (int, optional): Maximum number of retry attempts. Defaults to 3
            retry_delay (float, optional): Delay between retries in seconds. Defaults to 0.5
            segment_delay (float, optional): Delay after successful download. Defaults to 0

        Returns:
            bool: True if download was successful, False otherwise

        This function attempts to download a segment with retry logic for robustness.
        It handles authentication via cookies or stream keys, and includes proper
        error handling for network issues and invalid credentials.
        """
        global kill
        with download_semaphore:
            for retry_count in range(max_retries + 1):
                try:
                    # show downloading segments if args debug is set
                    if args.debug:
                        print(f"\n\n\nDownloading segment: {segment_url}\n\n")
                    response = (
                        requests.get(
                            segment_url, stream=True, cookies=cookies, params=params
                        )
                        if cookies
                        else requests.get(segment_url, stream=True, params=params)
                    )

                    # Check for successful response
                    if response.status_code == 200:
                        with open(output_path, "wb") as file:
                            for chunk in response.iter_content(chunk_size=16000):
                                file.write(chunk)
                        # time.sleep(segment_delay)  # Optional delay
                        return True
                    elif response.status_code == 401:
                        print(
                            "Invalid credentials. Please check your cookies/streamkey and try again."
                        )
                        input("Press CTRL+C to exit...")
                        kill = True
                        raise Exception("Exiting due to invalid credentials")
                    else:
                        print(
                            f"Failed to download segment, status code: {response.status_code}. Retrying {retry_count}/{max_retries}"
                        )
                except requests.exceptions.RequestException as e:
                    print(
                        f"Network error: {e}. Retrying {retry_count}/{max_retries} in {retry_delay} seconds..."
                    )
                    time.sleep(retry_delay)
                except Exception as e:
                    print(f"Unexpected error downloading segment: {e}")
                    break

        print(
            f"Failed to download segment {segment_url} after {max_retries} retries. Skipping."
        )
        # Clean up partial file if exists
        if os.path.exists(output_path):
            os.remove(output_path)
        return False

    def load_m3u8_with_retry(hls_url, retry_delay=5):
        """
        Load and parse an M3U8 playlist with retry logic.

        Args:
            hls_url (str): URL of the M3U8 playlist to load
            retry_delay (int, optional): Delay between retries in seconds. Defaults to 5

        Returns:
            m3u8.M3U8: Parsed M3U8 playlist object, or None if loading fails or shutdown is requested

        This function handles various network errors that may occur while loading
        the M3U8 playlist, implementing retry logic with configurable delay.
        It also supports multi-line URLs by taking the first line.
        """
        while not shutdown_flag:
            try:
                # Split and take first URL if multiple URLs are provided
                cleaned_url = hls_url.strip().split('\n')[0]
                if args.debug:
                    print(f"\n[DEBUG] Loading m3u8 from URL: {cleaned_url}")
                
                m3u8_obj = m3u8.load(cleaned_url)
                return m3u8_obj
            except (
                http.client.RemoteDisconnected,
                http.client.IncompleteRead,
                requests.exceptions.RequestException,
            ) as e:
                print(
                    f"Error loading m3u8 file: {e}. Retrying in {retry_delay} seconds..."
                )
                time.sleep(retry_delay)
            except Exception as e:
                print(f"Unexpected error loading m3u8 file: {e}")
                time.sleep(retry_delay)
        return None

    def generate_segment_filename(url, counter, task_id):
        """
        Generate a unique filename for a downloaded HLS segment.

        Args:
            url (str): URL of the HLS segment
            counter (int): Sequential counter for segment ordering
            task_id (str): Unique identifier for the transcription task

        Returns:
            str: Generated filename including task ID, counter, and URL hash

        The function creates a filename that includes:
        - Task ID to group segments from the same transcription
        - Counter for sequential ordering (zero-padded to 5 digits)
        - MD5 hash of URL to ensure uniqueness
        """
        url_hash = hashlib.md5(url.encode()).hexdigest()
        return os.path.join(temp_dir, f"{task_id}_{counter:05d}_{url_hash}.ts")

    def combine_audio_segments(segment_paths, output_path):
        """
        Combine multiple HLS segments into a single audio file.

        Args:
            segment_paths (list[str]): List of paths to segment files to combine
            output_path (str): Path where the combined file will be saved

        The function reads each segment file in binary mode and writes them
        sequentially to create a single combined file. It handles missing
        files gracefully and cleans up individual segment files after combining.
        """
        with open(output_path, "wb") as outfile:
            for segment_path in segment_paths:
                if not os.path.exists(segment_path):
                    print(f"Warning: File {segment_path} does not exist, skipping.")
                    continue
                try:
                    with open(segment_path, "rb") as infile:
                        outfile.write(infile.read())
                    os.remove(segment_path)
                except Exception as e:
                    print(f"Error combining audio segments: {e}")

    def translate_audio(file_path, model):
        """
        Translate audio content to English using Whisper model.

        Args:
            file_path (str): Path to the audio file to translate
            model (whisper.Whisper): Loaded Whisper model instance

        Returns:
            str: Translated text in English, or empty string if translation fails

        Uses Whisper's translate task to directly translate audio to English text.
        Includes fp16 optimization and previous text conditioning based on arguments.
        """
        try:
            result = model.transcribe(file_path, task="translate", fp16=args.fp16, language="English", condition_on_previous_text=args.condition_on_previous_text)
            return result["text"]
        except RuntimeError as e:
            print(f"Error transcribing audio: {e}")
            return ""

    def transcribe_audio(file_path, model, language):
        """
        Transcribe audio content in a specified language using Whisper model.

        Args:
            file_path (str): Path to the audio file to transcribe
            model (whisper.Whisper): Loaded Whisper model instance
            language (str): Language code for transcription

        Returns:
            str: Transcribed text in specified language, or empty string if transcription fails

        Uses Whisper's transcribe task with specified language, fp16 optimization,
        and previous text conditioning based on arguments.
        """
        try:
            result = model.transcribe(file_path, language=language, fp16=args.fp16, condition_on_previous_text=args.condition_on_previous_text)
            return result["text"]
        except RuntimeError as e:
            print(f"Error transcribing audio: {e}")
            return ""

    def detect_language(file_path, model, device=args.device):
        """
        Detect the language of audio content using Whisper model.

        Args:
            file_path (str): Path to the audio file to analyze
            model (whisper.Whisper): Loaded Whisper model instance
            device (str): Device to run inference on (CPU/CUDA). Defaults to args.device

        Returns:
            str: Detected language code, or "n/a" if detection fails

        Processes audio through mel spectrogram generation with adaptive n_mels
        based on RAM configuration (128 for 12gb-v3, 80 otherwise) before
        performing language detection.
        """
        try:
            audio = whisper.load_audio(file_path)
            audio = whisper.pad_or_trim(audio)
            
            # Use 128 mel bands for large-v3 model
            if args.ram == "11gb-v3":
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


    def process_audio(file_path, model):
        """
        Process audio file through transcription, translation, and output handling.

        Args:
            file_path (str): Path to the audio file to process
            model (whisper.Whisper): Loaded Whisper model instance

        This function orchestrates the complete audio processing workflow:
        1. Original language transcription (if enabled)
        2. English translation (if tasktranslate_task is True)
        3. Target language transcription (if tasktranscribe_task is True)
        
        Results are:
        - Printed to console with visual separators
        - Sent to Discord webhook if configured
        - Updated in API backend if port number is set
        
        The audio file is automatically cleaned up after processing.
        """
        if not os.path.exists(file_path):
            print(f"Warning: File {file_path} does not exist, skipping.")
            return

        transcription = None
        translation = None
        if args.stream_original_text:
            if args.stream_language:
                detected_language = stream_language
                # print(f"Language Set By Args: {detected_language}")
            else:
                # print("Testing for Language")
                detected_language = detect_language(file_path, model)
                # print(f"Language is: {detected_language}")
            transcription = transcribe_audio(
                file_path, model, language=detected_language
            )
            print(f"{'-' * 50} {detected_language} Original {'-' * 50}")
            print(transcription)
            if args.portnumber and transcription.strip():
                new_header = f"{transcription}"
                api_backend.update_header(new_header)

        if tasktranslate_task:
            translation = translate_audio(file_path, model)
            if translation:
                print(f"{'-' * 50} Stream EN Translation {'-' * 50}")
                print(translation)
                if webhook_url:
                    send_to_discord_webhook(
                        webhook_url, f"Stream EN Translation:\n{translation}\n"
                    )
                if args.portnumber:
                    new_header = f"{translation}"
                    api_backend.update_translated_header(new_header)

        if tasktranscribe_task:
            transcription = transcribe_audio(
                file_path, model, language=target_language
            )
            if transcription:
                print(
                    f"{'-' * 50} Stream {target_language} Transcription {'-' * 50}"
                )
                print(transcription)
                if webhook_url:
                    send_to_discord_webhook(
                        webhook_url,
                        f"Stream {target_language} Transcription:\n{transcription}\n",
                    )
                if args.portnumber and transcription.strip():
                    new_header = f"{transcription}"
                    api_backend.update_transcribed_header(new_header)
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
        except Exception as e:
            print(f"Error removing file {file_path}: {e}")

    def process_audio_thread():
        """
        Background thread function for processing audio segments.

        This thread continuously monitors the audio queue for new segments to process.
        When a segment is available, it calls process_audio() to handle transcription
        and translation. The thread runs until either:
        - shutdown_flag is set to True
        - None is received in the queue (signal to stop)

        This threaded approach allows concurrent downloading and processing of audio
        segments, improving overall throughput of the transcription system.
        """
        while not shutdown_flag:
            file_path = audio_queue.get()
            if file_path is None:
                break
            process_audio(file_path, model_name)

    # Start processing thread
    processing_thread = threading.Thread(target=process_audio_thread)
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

            # Get total segments and calculate starting point
            total_segments = len(m3u8_obj.segments)
            if total_segments == 0:
                if args.debug:
                    print("\n[DEBUG] Playlist is empty, waiting for segments...")
                time.sleep(1)  # Wait if playlist is empty
                continue

            # Start from the most recent segments on first run
            if len(downloaded_segments) == 0:
                start_idx = max(0, total_segments - segments_max)
                if args.debug:
                    print(f"\n[DEBUG] First run:")
                    print(f"[DEBUG] Total segments in playlist: {total_segments}")
                    print(f"[DEBUG] Starting from segment index: {start_idx}")
                    print(f"[DEBUG] Will process {total_segments - start_idx} segments")
            else:
                start_idx = 0
                if args.debug:
                    print(f"\n[DEBUG] Continuing run:")
                    print(f"[DEBUG] Total segments in playlist: {total_segments}")
                    print(f"[DEBUG] Previously downloaded segments: {len(downloaded_segments)}")
                    print(f"[DEBUG] Starting from beginning to check for new segments")

            # Process segments from the calculated starting point
            for idx in range(start_idx, total_segments):
                segment = m3u8_obj.segments[idx]
                if segment.uri in downloaded_segments:
                    continue  # Skip already downloaded segments

                segment_path = generate_segment_filename(
                    segment.uri, counter, task_id
                )
                counter += 1
                try:
                    if args.debug:
                        print(f"\n[DEBUG] Attempting to download segment {counter}:")
                        print(f"[DEBUG] Segment URI: {segment.uri}")

                    if download_segment(segment.absolute_uri, segment_path):
                        if kill:
                            break
                        downloaded_segments.add(segment.uri)
                        accumulated_segments.append(segment_path)

                        if args.debug:
                            print(f"[DEBUG] Successfully downloaded segment {counter}")
                            print(f"[DEBUG] Accumulated segments: {len(accumulated_segments)}/{segments_max}")

                        if len(accumulated_segments) >= segments_max:
                            if args.debug:
                                print(f"[DEBUG] Reached max segments ({segments_max}), processing batch...")
                            combined_path = os.path.join(
                                temp_dir, f"{task_id}_combined_{counter}.ts"
                            )
                            combine_audio_segments(
                                accumulated_segments, combined_path
                            )
                            audio_queue.put(combined_path)
                            accumulated_segments = []
                except Exception as e:  # Catch the raised exception
                    print(f"Error during download: {e}")
                    break  # Exit the loop

    except KeyboardInterrupt:
        shutdown_flag = True  # Signal to shut down

    except Exception as e:
        exit(0)

    # Cleanup
    for file in os.listdir(temp_dir):
        os.remove(os.path.join(temp_dir, file))
    audio_queue.put(None)  # Signal processing thread to stop
    processing_thread.join()


def stop_transcription():
    """
    Stop the transcription process gracefully.

    Sets the global shutdown flag to True, which signals various components to stop:
    - M3U8 playlist loading loop
    - Audio processing thread
    - Main segment downloading loop
    
    After this is called, the transcription system will:
    1. Complete processing of current segments
    2. Clean up temporary files
    3. Join the processing thread
    4. Exit cleanly
    """
    global shutdown_flag
    shutdown_flag = True


print("Stream Transcription Module Loaded")