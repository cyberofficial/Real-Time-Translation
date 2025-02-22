from __future__ import annotations
import io
import re
import shutil
from datetime import datetime, timedelta
from queue import Queue
from tempfile import NamedTemporaryFile
from time import sleep
from typing import Optional, Dict, List, Tuple, Any

import whisper
import torch
import speech_recognition as sr
from colorama import Fore, Style

from modules.discord import send_to_discord_webhook
from modules.console_settings import set_window_title
from modules import api_backend
from modules.languages import get_valid_languages

class TranscriptionCore:
    """Core class for handling audio transcription, translation, and processing.
    
    This class manages the complete pipeline of audio processing including:
    - Audio data collection and processing
    - Language detection
    - Transcription
    - Translation (if enabled)
    - Result filtering and display
    
    Attributes:
        args: Command line arguments
        device: PyTorch device (CPU/CUDA)
        audio_model: Whisper model instance
        blacklist: List of words to filter from output
        transcription: List of processed transcriptions
        phrase_time: Timestamp of last phrase
        last_sample: Raw audio data buffer
        detected_language: Detected source language
        original_text: Original transcribed text
        translated_text: Translated text (if enabled)
        transcribed_text: Text transcribed to target language (if enabled)
    """
    
    def __init__(self, args: Any, device: torch.device,
                 audio_model: whisper.Whisper, blacklist: List[str]) -> None:
        """Initialize the TranscriptionCore.
        
        Args:
            args: Parsed command line arguments
            device: PyTorch device for model execution
            audio_model: Loaded Whisper model instance
            blacklist: List of words to filter from output
        """
        self.args = args
        self.device = device
        self.audio_model = audio_model
        self.blacklist = blacklist
        self.transcription: List[Tuple[Optional[str], Optional[str], Optional[str], Optional[str]]] = ['']
        self.phrase_time: Optional[datetime] = None
        self.last_sample: bytes = bytes()
        self.detected_language: Optional[str] = None
        self.original_text: Optional[str] = None
        self.translated_text: Optional[str] = None
        self.transcribed_text: Optional[str] = None

    def process_audio(self, data_queue: Queue, source: sr.AudioSource,
                     temp_file: str) -> bool:
        """Process audio data from the queue.
        
        Args:
            data_queue: Queue containing raw audio data
            source: Audio source for recording
            temp_file: Path to temporary file for audio processing
            
        Returns:
            bool: True if processing should continue, False if an error occurred
            
        Raises:
            Exception: If an error occurs during audio processing
        """
        try:
            now = datetime.utcnow()
            if not data_queue.empty():
                if not self.args.no_log:
                    print("\nAudio stream detected...")
                
                phrase_complete = self._handle_phrase_timeout(now)
                self._collect_audio_data(data_queue)
                self._process_audio_file(source, temp_file)
                
                if phrase_complete:
                    self.transcription.append((self.original_text, 
                                            self.translated_text if self.args.translate else None,
                                            self.transcribed_text if self.args.transcribe else None,
                                            self.detected_language))
                else:
                    self.transcription[-1] = (self.original_text,
                                           self.translated_text if self.args.translate else None,
                                           self.transcribed_text if self.args.transcribe else None,
                                           self.detected_language)
                
                self._update_api_headers()
                self._display_results()

            sleep(0.5)
            return True
            
        except Exception as e:
            print(f"Error in process_audio: {str(e)}")
            return False

    def _handle_phrase_timeout(self, now: datetime) -> bool:
        """Check if the current phrase has timed out.
        
        Args:
            now: Current timestamp

        Returns:
            bool: True if phrase has timed out, False otherwise
        """
        if self.phrase_time and now - self.phrase_time > timedelta(seconds=self.args.phrase_timeout):
            self.last_sample = bytes()
            return True
        self.phrase_time = now
        return False

    def _collect_audio_data(self, data_queue: Queue) -> None:
        """Collect audio data from the queue and accumulate in last_sample buffer.
        
        Args:
            data_queue: Queue containing raw audio data chunks
        """
        while not data_queue.empty():
            data = data_queue.get()
            self.last_sample += data

    def _process_audio_file(self, source: sr.AudioSource, temp_file: str) -> None:
        """Process the audio file and perform transcription/translation.
        
        This method orchestrates the complete audio processing pipeline:
        1. Prepare audio data from the buffer
        2. Save to temporary file
        3. Perform initial transcription
        4. Handle translation if enabled
        5. Handle target language transcription if enabled
        
        Args:
            source: Audio source for sample rate information
            temp_file: Path to temporary file for audio processing
        """
        audio_data = self._prepare_audio_data(source)
        self._save_audio_data(audio_data, temp_file)
        self._perform_transcription(temp_file)
        
        if self.args.translate:
            self._perform_translation(temp_file)
            
        if self.args.transcribe:
            self._perform_transcription_to_target(temp_file)

    def _prepare_audio_data(self, source: sr.AudioSource) -> sr.AudioData:
        """Convert raw audio data to AudioData object.
        
        Args:
            source: Audio source containing sample rate and width information
            
        Returns:
            sr.AudioData: Processed audio data ready for transcription
        """
        return sr.AudioData(self.last_sample, source.SAMPLE_RATE, source.SAMPLE_WIDTH)

    def _save_audio_data(self, audio_data: sr.AudioData, temp_file: str) -> None:
        """Save audio data to a temporary WAV file.
        
        Args:
            audio_data: Processed audio data
            temp_file: Path to save the temporary WAV file
            
        Raises:
            IOError: If there's an error writing to the file
        """
        with io.BytesIO(audio_data.get_wav_data()) as wav_data:
            with open(temp_file, 'w+b') as f:
                shutil.copyfileobj(wav_data, f)

    def _perform_transcription(self, temp_file: str) -> None:
        """Process audio file and perform initial transcription.
        
        This method handles the complete transcription process:
        1. Load and preprocess the audio file
        2. Generate mel spectrogram
        3. Detect the language
        4. Perform transcription
        
        Args:
            temp_file: Path to the temporary audio file
        """
        audio = whisper.load_audio(temp_file)
        audio = whisper.pad_or_trim(audio)
        mel = whisper.log_mel_spectrogram(
            audio,
            n_mels=128 if self.args.ram == "11gb-v3" else 80
        ).to(self.device)

        self._detect_language(mel)
        
        result = self._transcribe_audio(temp_file)
        self.original_text = result['text'].strip()

    def _detect_language(self, mel: torch.Tensor) -> None:
        """Detect or determine the language of the audio input.
        
        This method determines the language through one of these methods:
        1. Use English if model is English-specific
        2. Use stream language if specified
        3. Use explicitly set language if provided
        4. Detect language using the model
        
        Args:
            mel: Mel spectrogram of the audio input
        """
        if ".en" in self.args.model:
            self.detected_language = "English"
        elif self.args.stream_language:
            print(f"Language Set: {self.args.stream_language}\n")
            self.detected_language = self.args.stream_language
        elif self.args.language:
            self.detected_language = self.args.language
        else:
            if not self.args.no_log:
                print(f"Detecting Language\n")
            _, language_probs = self.audio_model.detect_language(mel)
            self.detected_language = max(language_probs, key=language_probs.get)
            self._update_language_confidence(language_probs)

    def _update_language_confidence(self, language_probs: Dict[str, float]) -> None:
        """Update and display the confidence level for detected language.
        
        Args:
            language_probs: Dictionary mapping language codes to confidence scores
        
        Raises:
            KeyError: If detected language is not found in probability dictionary
        """
        try:
            confidence = language_probs[self.detected_language] * 100
            confidence_color = (Fore.GREEN if confidence > 75
                               else (Fore.YELLOW if confidence > 50 else Fore.RED))
            set_window_title(self.detected_language, confidence)
            if not self.args.no_log:
                print(f"Detected language: {self.detected_language} "
                      f"{confidence_color}({confidence:.2f}% Accuracy){Style.RESET_ALL}")
        except KeyError:
            print(f"Warning: Could not determine confidence for language {self.detected_language}")
        except Exception as e:
            print(f"Error updating language confidence: {str(e)}")

    def _transcribe_audio(self, temp_file: str) -> Dict[str, Any]:
        """Transcribe audio file using the Whisper model.
        
        Args:
            temp_file: Path to the temporary audio file
            
        Returns:
            Dict[str, Any]: Transcription result containing text and metadata
            
        Note:
            Will retry transcription once if result is empty and retry flag is set
        """
        # Handle FP16 settings properly
        dtype = torch.float16 if self.args.fp16 else torch.float32
        if self.device == torch.device("cpu"):
            if torch.cuda.is_available():
                print("Warning: Performing inference on CPU when CUDA is available")
            if dtype == torch.float16:
                print("Warning: FP16 is not supported on CPU; using FP32 instead")
                dtype = torch.float32

        kwargs = {
            'language': self.detected_language,
            'condition_on_previous_text': self.args.condition_on_previous_text,
            'fp16': dtype == torch.float16
        }
            
        result = self.audio_model.transcribe(temp_file, **kwargs)
        
        if not self.args.no_log:
            print(f"Detected Speech: {result['text']}")
            
        if result['text'] == "" and self.args.retry:
            if not self.args.no_log:
                print("Transcription failed, trying again...")
            result = self.audio_model.transcribe(temp_file, **kwargs)
            if not self.args.no_log:
                print(f"Detected Speech: {result['text']}")
                
        return result

    def _perform_translation(self, temp_file: str) -> None:
        """Translate non-English audio content to English.
        
        Args:
            temp_file: Path to the temporary audio file
            
        Note:
            - Only processes if detected language is not English
            - Will retry once if translation fails and retry flag is set
            - Updates self.translated_text with the result
        """
        self.translated_text = ""
        if self.detected_language != 'en':
            if not self.args.no_log:
                print("Translating...")
            # Handle FP16 settings properly
            dtype = torch.float16 if self.args.fp16 else torch.float32
            if self.device == torch.device("cpu"):
                if torch.cuda.is_available():
                    print("Warning: Performing inference on CPU when CUDA is available")
                if dtype == torch.float16:
                    print("Warning: FP16 is not supported on CPU; using FP32 instead")
                    dtype = torch.float32

            kwargs = {
                'task': 'translate',
                'language': self.detected_language,
                'condition_on_previous_text': self.args.condition_on_previous_text,
                'fp16': dtype == torch.float16
            }
                
            translated_result = self.audio_model.transcribe(temp_file, **kwargs)
            self.translated_text = translated_result['text'].strip()
            
            if self.translated_text == "" and self.args.retry:
                if not self.args.no_log:
                    print("Translation failed, trying again...")
                translated_result = self.audio_model.transcribe(temp_file, **kwargs)
                self.translated_text = translated_result['text'].strip()

    def _perform_transcription_to_target(self, temp_file: str) -> None:
        """Transcribe audio to the specified target language.
        
        Args:
            temp_file: Path to the temporary audio file
            
        Note:
            - Will retry once if transcription fails and retry flag is set
            - Updates self.transcribed_text with the result
        """
        if not self.args.no_log:
            print(f"Transcribing to {self.args.target_language}...")
            
        # Handle FP16 settings properly
        dtype = torch.float16 if self.args.fp16 else torch.float32
        if self.device == torch.device("cpu"):
            if torch.cuda.is_available():
                print("Warning: Performing inference on CPU when CUDA is available")
            if dtype == torch.float16:
                print("Warning: FP16 is not supported on CPU; using FP32 instead")
                dtype = torch.float32

        kwargs = {
            'task': 'transcribe',
            'language': self.args.target_language,
            'condition_on_previous_text': self.args.condition_on_previous_text,
            'fp16': dtype == torch.float16
        }
            
        transcribed_result = self.audio_model.transcribe(temp_file, **kwargs)
        self.transcribed_text = transcribed_result['text'].strip()
        
        if self.transcribed_text == "" and self.args.retry:
            if not self.args.no_log:
                print("Transcribe failed, trying again...")
            transcribed_result = self.audio_model.transcribe(temp_file, **kwargs)
            self.transcribed_text = transcribed_result['text'].strip()

    def _update_api_headers(self) -> None:
        """Check if API port is specified and update headers."""
        if self.args.portnumber:
            self._update_filtered_headers()

    def _update_filtered_headers(self) -> None:
        """Update API backend headers with filtered transcription results.
        
        This method updates the backend headers with filtered versions of:
        - Original transcription
        - Translated text (if available)
        - Target language transcription (if available)
        
        Note:
            Catches and logs any errors that occur during header updates
        """
        try:
            filtered_header_text = self._filter_text(self.original_text)
            api_backend.update_header(filtered_header_text)
            
            if self.translated_text:
                filtered_translated_text = self._filter_text(self.translated_text)
                api_backend.update_translated_header(filtered_translated_text)
                
            if self.transcribed_text:
                filtered_transcribed_text = self._filter_text(self.transcribed_text)
                api_backend.update_transcribed_header(filtered_transcribed_text)
        except Exception as e:
            print(f"Warning: Failed to update API headers: {str(e)}")

    def _filter_text(self, text: Optional[str]) -> str:
        """Filter text by removing blacklisted words.
        
        Args:
            text: Input text to filter, can be None
            
        Returns:
            str: Filtered text with blacklisted words removed,
                 or empty string if input is None
        """
        filtered_text = text.lower()
        for phrase in self.blacklist:
            filtered_text = re.sub(rf"\b{phrase.lower()}\b", "", filtered_text).strip()
        return filtered_text

    def _display_results(self) -> None:
        """Display the current transcription results.
        
        This method handles the display logic by:
        1. Filtering the original text
        2. Choosing between full or simple display format based on no_log flag
        3. Displaying the results in the chosen format
        
        Note:
            Will not display anything if filtered text is empty
        """
        filtered_text = self._filter_text(self.original_text)
        
        if filtered_text:
            if not self.args.no_log:
                self._display_full_results(filtered_text)
            else:
                self._display_simple_results(filtered_text)

    def _display_full_results(self, filtered_text: str) -> None:
        """Display detailed results with formatted layout.
        
        Displays the original transcription, translation (if available),
        and target language transcription (if available) with visual separators
        and proper formatting.
        
        Args:
            filtered_text: Filtered transcription text to display
        """
        print("=" * shutil.get_terminal_size().columns)
        print(f"{' ' * int((shutil.get_terminal_size().columns - 15) / 2)} "
              f"What was Heard -> {self.detected_language} "
              f"{' ' * int((shutil.get_terminal_size().columns - 15) / 2)}")
        print(filtered_text)

        if self.args.translate and self.translated_text:
            filtered_translated = self._filter_text(self.translated_text)
            print(f"{'-' * int((shutil.get_terminal_size().columns - 15) / 2)} "
                  f"EN Translation "
                  f"{'-' * int((shutil.get_terminal_size().columns - 15) / 2)}")
            print(f"{filtered_translated}\n")

        if self.args.transcribe and self.transcribed_text:
            filtered_transcribed = self._filter_text(self.transcribed_text)
            print(f"{'-' * int((shutil.get_terminal_size().columns - 15) / 2)} "
                  f"{self.detected_language} -> {self.args.target_language} "
                  f"{'-' * int((shutil.get_terminal_size().columns - 15) / 2)}")
            print(f"{filtered_transcribed}\n")

    def _display_simple_results(self, filtered_text: str) -> None:
        """Display simplified one-line results for each component.
        
        Displays each available component (original text, translation,
        and target language transcription) on separate lines with
        minimal formatting.
        
        Args:
            filtered_text: Filtered transcription text to display
        """
        print(f"[Input ({self.detected_language})]: {filtered_text}\n")
        
        if self.args.transcribe and self.transcribed_text:
            filtered_transcribed = self._filter_text(self.transcribed_text)
            print(f"[Transcription ({self.detected_language} -> "
                  f"{self.args.target_language})]: {filtered_transcribed}\n")
            
        if self.args.translate and self.translated_text:
            filtered_translated = self._filter_text(self.translated_text)
            print(f"[Translation (EN)]: {filtered_translated}\n")