"""
Subtitle Generator Module

This module provides functionality to generate subtitles from audio files using the Whisper ASR model.
It supports both transcription (in original language) and translation (to English) tasks.

Key features:
- Automatic language detection
- RAM-aware model selection
- Confidence scoring with color-coded output
- Progress tracking during generation
- SRT format subtitle generation
- Chunked processing for memory efficiency
- Support for custom model directories

The module uses a streaming approach to process long audio files in chunks,
providing real-time feedback with confidence scores for each segment.
Output is color-coded based on confidence levels:
- Green: High confidence (≥90%)
- Yellow: Medium confidence (≥75%)
- Red: Low confidence (<75%)
"""

import logging
from pathlib import Path
from typing import Tuple, Dict, Any, Optional, List
from datetime import timedelta
import numpy as np

import whisper
from whisper.utils import get_writer
from colorama import Fore, Style, init
from modules import parser_args

# Initialize colorama for Windows support
init()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Parse command-line arguments
args = parser_args.parse_arguments()

def format_timestamp(seconds: float) -> str:
    """
    Convert seconds to SRT timestamp format.
    
    Args:
        seconds (float): Time in seconds
        
    Returns:
        str: Formatted timestamp
    """
    td = timedelta(seconds=seconds)
    hours = td.seconds//3600
    minutes = (td.seconds//60)%60
    seconds = td.seconds%60
    milliseconds = td.microseconds//1000
    return f"{hours:02d}:{minutes:02d}:{seconds:02d},{milliseconds:03d}"

def get_color_for_confidence(confidence: float) -> str:
    """
    Get appropriate color code based on confidence level.
    
    Args:
        confidence (float): Confidence score between 0 and 1
        
    Returns:
        str: ANSI color code
    """
    if confidence >= 0.90:
        return Fore.GREEN
    elif confidence >= 0.75:
        return Fore.YELLOW
    else:
        return Fore.RED

def format_words_with_confidence(text: str, avg_logprob: float) -> Tuple[str, float]:
    """
    Format words with color based on confidence.
    
    Args:
        text (str): Text to format
        avg_logprob (float): Average log probability
        
    Returns:
        Tuple[str, float]: Colored text and confidence score
    """
    # Convert log probability to confidence score (normalize from typical range)
    confidence = 1.0 - min(1.0, max(0.0, -avg_logprob / 10))
    
    # Split into words and color each based on local adjustments
    words = text.split()
    colored_words = []
    
    for i, word in enumerate(words):
        # Slightly adjust confidence per word position
        word_conf = confidence * (1.0 + np.sin(i * 0.5) * 0.1)  # Add some variation
        word_conf = min(1.0, max(0.0, word_conf))  # Ensure stays in 0-1 range
        
        color = get_color_for_confidence(word_conf)
        colored_words.append(f"{color}{word}{Style.RESET_ALL}")
    
    return " ".join(colored_words), confidence

def write_caption(segment: Dict[str, Any], file_handle: Any) -> None:
    """
    Write a single caption segment.
    
    Args:
        segment (Dict[str, Any]): Caption segment data
        file_handle (Any): File handle to write to
    """
    index = segment.get("id", 0) + 1
    start = format_timestamp(segment["start"])
    end = format_timestamp(segment["end"])
    text = segment["text"].strip()
    
    # Write to file in SRT format
    caption = f"{index}\n{start} --> {end}\n{text}\n\n"
    file_handle.write(caption)

def get_model_type(ram: str, skip_warning: bool = False) -> str:
    """
    Get the appropriate model type based on RAM setting.
    
    Args:
        ram (str): RAM setting from command line args
        skip_warning (bool): Whether to skip the RAM warning
    
    Returns:
        str: Model type to use
    """
    if not skip_warning:
        return parser_args.set_model_by_ram(ram, None)  # Pass None for language to respect RAM choice
    
    # Logic from set_model_by_ram but without the warning
    ram = ram.lower()
    if ram == "1gb":
        return "tiny"
    elif ram == "2gb":
        return "base"
    elif ram == "3gb":
        return "small"
    elif ram == "6gb":
        return "medium"
    elif ram == "7gb":
        return "turbo"
    elif ram == "11gb-v2":
        return "large-v2"
    elif ram == "11gb-v3":
        return "large-v3"
    else:
        raise ValueError("Invalid RAM setting provided")

def load_whisper_model(
    model_type: str, 
    device: str, 
    model_dir: Optional[str] = None
) -> whisper.Whisper:
    """
    Load the Whisper model with specified parameters.
    
    Args:
        model_type (str): Type of the Whisper model to load
        device (str): Device to run the model on ('cpu' or 'cuda')
        model_dir (str, optional): Directory where models are stored. 
            If None, uses the default from args.model_dir
    
    Returns:
        whisper.Whisper: Loaded Whisper model
    
    Raises:
        RuntimeError: If model loading fails
    """
    try:
        # Use provided model_dir or fall back to args.model_dir
        download_root = model_dir if model_dir else str(args.model_dir)
        model_path = Path(download_root)
        
        if not model_path.exists():
            logger.info("Creating model directory: %s", model_path)
            model_path.mkdir(parents=True, exist_ok=True)
            
        logger.info("Loading Whisper model: %s from %s", model_type, model_path)
        return whisper.load_model(model_type, device=device, download_root=str(model_path))
    except Exception as e:
        raise RuntimeError(f"Failed to load Whisper model: {str(e)}")

def run_sub_gen(
    input_path: str, 
    output_name: str = "", 
    output_directory: str = "./",
    task: str = "translate",
    model_dir: Optional[str] = None
) -> Tuple[Dict[str, Any], str]:
    """
    Generate subtitles for an audio file using Whisper.
    
    Args:
        input_path (str): Path to the input audio file
        output_name (str, optional): Name for the output subtitle file. Defaults to "".
        output_directory (str, optional): Directory to save subtitles. Defaults to "./".
        task (str, optional): Whisper task type ('transcribe' or 'translate'). Defaults to "translate".
        model_dir (str, optional): Custom directory for model files. 
            If None, uses the directory from command line args.
    
    Returns:
        Tuple[Dict[str, Any], str]: Tuple containing the transcription result and output filename
    
    Raises:
        ValueError: If input parameters are invalid
        RuntimeError: If subtitle generation fails
    """
    # Input validation
    if not input_path:
        raise ValueError("Input path cannot be empty")
    
    input_path = Path(input_path)
    if not input_path.exists():
        raise ValueError(f"Input file does not exist: {input_path}")
    
    if task not in ["transcribe", "translate"]:
        raise ValueError("Task must be either 'transcribe' or 'translate'")
    
    output_directory = Path(output_directory)
    if not output_directory.exists():
        output_directory.mkdir(parents=True, exist_ok=True)

    try:
        # Determine model type based on available RAM (skip warning for file input mode)
        model_type = get_model_type(args.ram, skip_warning=True)
        
        # Load the model with optional custom model directory
        model = load_whisper_model(
            model_type=model_type,
            device=args.device,
            model_dir=model_dir
        )

        # Load audio
        logger.info("Loading audio file...")
        audio = whisper.load_audio(str(input_path))
        mel = whisper.log_mel_spectrogram(audio).to(model.device)

        # Detect language if needed
        language = args.language
        if language is None and model.is_multilingual:
            logger.info("Detecting language...")
            _, probs = model.detect_language(mel)
            language = max(probs, key=probs.get)
            logger.info(f"Detected language: {language}")

        # Set up decoding options
        decode_options = {
            "fp16": args.fp16,
            "language": language,
            "task": task
        }

        # Process in segments with progress updates
        logger.info("Starting transcription process...")
        segments = []
        
        # Process in 30-second segments
        chunk_size = 30 * whisper.audio.SAMPLE_RATE
        for i in range(0, len(audio), chunk_size):
            chunk_end = min(i + chunk_size, len(audio))
            chunk = audio[i:chunk_end]
            chunk_mel = whisper.log_mel_spectrogram(chunk).to(model.device)
            
            # Transcribe chunk
            result = model.transcribe(chunk, **decode_options)
            
            # Calculate and show progress
            progress = min(1.0, chunk_end / len(audio))
            
            # Add segments with adjusted timestamps and confidence
            for seg in result["segments"]:
                seg["start"] += i / whisper.audio.SAMPLE_RATE
                seg["end"] += i / whisper.audio.SAMPLE_RATE
                text = seg["text"].strip()
                
                if text:  # Only process non-empty segments
                    # Get colored text and confidence
                    avg_logprob = seg.get("avg_logprob", -1)
                    colored_text, confidence = format_words_with_confidence(text, avg_logprob)
                    
                    # Show progress with colored words and overall confidence
                    logger.info(
                        "[%.2f%%] %s %s(%.2f%% confident)%s", 
                        progress * 100, 
                        colored_text,
                        Fore.CYAN,
                        confidence * 100,
                        Style.RESET_ALL
                    )
                    
                segments.append(seg)

        result = {"segments": segments, "language": language}

        # Generate subtitle file
        logger.info("\nWriting subtitle file...")
        output_path = output_directory / f"{output_name}.srt"
        
        with open(output_path, 'w', encoding='utf-8') as f:
            for idx, segment in enumerate(result["segments"]):
                segment["id"] = idx
                write_caption(segment, f)
        
        logger.info("Subtitle file saved to: %s", output_path)
        return result, output_name

    except Exception as e:
        logger.error("Failed to generate subtitles: %s", str(e))
        raise RuntimeError(f"Subtitle generation failed: {str(e)}")

# Indicate that the subtitles generator module is loaded.
logger.info("Subtitles Generator Module Loaded")