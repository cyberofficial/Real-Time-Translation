## Synthalingua 
<img src="https://github.com/cyberofficial/Synthalingua/assets/19499442/c81d2c51-bf85-4055-8243-e6a1262cce8a" width=70%>

## Wiki
Read the [wiki here](https://github.com/cyberofficial/Synthalingua/wiki)


## About

Synthalingua is an advanced, self-hosted tool that leverages the power of artificial intelligence to translate audio from various languages into English in near real time, offering the possibility of multilingual outputs. This innovative solution utilizes both GPU and CPU resources to handle the input transcription and translation, ensuring optimized performance. Although it is currently in beta and not perfect, Synthalingua is actively being developed and will receive regular updates to further enhance its capabilities.


## Developed Proudly in PyCharm IDE from JetBrains
JetBrains kindly approved me for an OSS licenses for their software for use of this project. This will grealty improve my production rate.

Learn about it here: [https://jb.gg/OpenSourceSupport](https://jb.gg/OpenSourceSupport?from=Synthalingua)

[<img src="https://resources.jetbrains.com/storage/products/company/brand/logos/jb_beam.png" width="15%">](https://www.jetbrains.com/?from=Synthalingua)
[<img src="https://resources.jetbrains.com/storage/products/company/brand/logos/PyCharm.png" width="35%">](https://www.jetbrains.com/pycharm/?from=Synthalingua)


## Grab the portable version on itch! It include the GUI.
[<img src="https://i.imgur.com/dyZz6u5.png" width=60%>](https://cyberofficial.itch.io/synthalingua)

### Badges
[![CodeQL](https://github.com/cyberofficial/Synthalingua/actions/workflows/codeql.yml/badge.svg)](https://github.com/cyberofficial/Synthalingua/actions/workflows/codeql.yml)

#### Readme will update as time goes. This is a work in progress.

### Table of Contents
| Table of Contents | Description |
| ----------------- | ----------- |
| [Disclaimer](#things-to-knowdisclaimerswarningsetc) | Things to know/Disclaimers/Warnings/etc |
| [To Do List](#todo) | Things to do |
| [Contributors](#contributors) | People who helped with the project or contributed to the project. |
| [Installing/Setup](#installation) | How to install and setup the tool. |
| Misc | [Usage and File Arguments](#usage) - [Examples](#examples) - [Web Server](#web-server) |
| [Troubleshooting](#troubleshooting) | Common issues and how to fix them. |
| [Additional Info](#additional-information) | Additional information about the tool. |
| [Video Demos](#video-demonstration) | Video demonstrations of the tool. |
| [Extra Notes](#things-to-note) | Extra notes about the tool. |

## Things to know/Disclaimers/Warnings/etc
This AI-powered translation tool is currently a work in progress and is actively being developed to improve its accuracy and functionality over time. Users should be aware that while the tool works effectively in many scenarios, it is not perfect and may occasionally produce translation errors or bugs. These issues are continuously being addressed where possible, and updates will be rolled out to enhance the tool's performance. For instance, you may encounter situations where the translation is slightly off or where technical glitches occur, but these are expected to diminish as improvements are made.

The accuracy of translations is significantly higher when the input speech is clear and slow. If the speaker talks too fast or mumbles, the tool might struggle to provide an accurate translation, although it will still attempt to offer a useful output. For example, when using the tool in a quiet environment with clear, deliberate speech, the results are generally more precise. However, in noisy settings or when the speech is rushed, you might see a drop in accuracy. Background noise, like loud music, can also interfere with the tool’s ability to translate effectively.

It’s important to note that this tool is designed for casual, non-professional use. It is ideal for purposes such as language learning, engaging in informal conversations, or understanding foreign content for entertainment. However, it is not intended for high-stakes or professional translations, such as legal documents, medical texts, or official communications. For example, while the tool can be fun and educational for learning a new language or watching foreign media, it should not be relied on for specialized or critical tasks where accuracy is paramount.

As a user, you are responsible for ensuring that the tool is used ethically and not for purposes like spreading misinformation or hate speech. If there is a discrepancy between the translation and the original speech, it's crucial that you verify the output before sharing it with others. For instance, if the tool produces a misleading translation, it is your responsibility to double-check the content before using it or distributing it further.

Users should also be aware that they are using the tool at their own risk. The repository owner cannot be held accountable for any damages, issues, or unintended consequences that arise from the use of this tool. For example, if the tool malfunctions or provides an inaccurate translation that leads to a misunderstanding, the developer(s)\contributors are not liable for any outcomes that occur as a result of this. You, as the user, assume all responsibility for your actions while using the tool.

This tool is not intended to replace human translators, particularly for complex or specialized content. While it may be helpful for casual and everyday use, a professional translator should be consulted for more intricate tasks, such as translating legal agreements or technical manuals. For example, if you need a precise translation of a business contract, it is recommended to seek assistance from a qualified human translator rather than relying solely on this tool.

In terms of performance, the tool’s effectiveness may vary depending on your hardware setup. A faster CPU or GPU will lead to better results, while slower systems may experience delays or reduced performance. However, other factors, such as internet connection speed or microphone quality, have a minimal effect on its functionality. For instance, if you're running the tool on a high-performance computer, you’ll likely experience smoother translations compared to using it on an older, slower machine.

Lastly, it's important to remember that this is a __tool__, **not a service**. If using it violates any platform’s terms of service or causes any issues, the responsibility falls solely on the user. For example, if the tool's use results in violating rules on a platform—such as using the tool to translate inappropriate language—you are accountable for any penalties or restrictions imposed as a result.

## TODO
| Todo  | Sub-Task                                                                                                                                                                                                                                               | Status |
|-------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|--------|
| Add support for AMD GPUs. | ROCm support - WSL 2.0/Linux Only                                                                                                                                                                                                                      | ✅      |
|       | OpenCL support - Linux Only                                                                                                                                                                                                                            | ✅      |
| Add support API access. |                                                                                                                                                                                                                                                        | ✅      |
| Custom localhost web server. |                                                                                                                                                                                                                                                        | ✅      |
| Add reverse translation. |                                                                                                                                                                                                                                                        | ✅      |
|       | Localize script to other languages. (Will take place after reverse translations.)                                                                                                                                                                      | ❌      |
| Custom dictionary support. |                                                                                                                                                                                                                                                        | ❌      |
| GUI.  |                                                                                                                                                                                                                                                        | ✅      |
| Sub Title Creation |                                                                                                                                                                                                                                                        | ✅      |
| Linux support. |                                                                                                                                                                                                                                                        | ✅      |
| Improve performance. |                                                                                                                                                                                                                                                        | ❌      |
|       | Compressed Model Format for lower ram users                                                                                                                                                                                                            | ✅      |
|       | Better large model loading speed                                                                                                                                                                                                                       | ✅      |
|          | Split model up into multiple chunks based on usage                                                                                                                                                                                                     | ❌      |
| Stream Audio from URL |                                                                                                                                                                                                                                                        | ✅      |
| Increase model swapping accuracy. |                                                                                                                                                                                                                                                        | ❌      |
| No Microphone Required | Streaming Module                                                                                                                                                                                                                                       | ✅      |
| Server Control Panel | Currently under work, will come out in a future release. I've want to get this out soon as possible, but I've been running into road blocks. This is a higher prio feature, please keep an eye out for a future dev blog on more details and previews! | 🚧     |


# Contributors 
## [Guidelines](https://github.com/cyberofficial/Synthalingua/contribute)
#### [@DaniruKun](https://github.com/DaniruKun) - https://watsonindustries.live
#### [@Expletive](https://github.com/Expletive) - https://evitelpxe.neocities.org 
#### [@Adenser](https://github.com/Adenser)

# System Requirements
| Supported GPUs | Description |
| -------------- | ----------- |
| Nvidia Dedicated Graphics | Supported |
| Nvidia Integrated Graphics | Tested - Not Supported |
| AMD/ATI | * Linux Verified |
| Intel Arc | Not Supported |
| Intel HD | Not Supported |
| Intel iGPU | Not Supported |

### GUI Portable Version (not the CLI portable)
* Minimum supported Windows Version is now Windows 10.0.17763
  * Windows 7 is no longer supported due to the change of .NET builds.
  * You may download the source code and change to Windows 7, but it's not suggested to keep using Windows 7.

You can find full list of supported Nvida GPUs here:
* [Official Nvidia List](https://developer.nvidia.com/cuda-gpus)
* [Simple List](https://gist.github.com/standaloneSA/99788f30466516dbcc00338b36ad5acf)

| Requirement | Minimum | Moderate | Recommended | Best Performance |
| ----------- | ------- | -------- | ----------- | ---------------- |
| CPU Cores | 2 | 6 | 8 | 16 |
| CPU Clock Speed (GHz) | 2.5 or higher | 3.0 or higher | 3.5 or higher | 4.0 or higher |
| RAM (GB) | 4 or higher | 8 or higher | 16 or higher | 16 or higher |
| GPU VRAM (GB) | 2 or higher | 6 or higher | 8 or higher | 12 or higher |
| Free Disk Space (GB) | 15 or higher | 15 or higher | 15 or higher | 15 or higher |
| GPU (suggested) As long as the gpu you have is within vram spec, it should work fine. | Nvidia GTX 1050 or higher | Nvidia GTX 1660 or higher | Nvidia RTX 3070 or higher | Nvidia RTX 3090 or higher |

Note:
- Nvidia GPU support on Linux and Windows
- Nvidia GPU is suggested but not required.
- AMD GPUs are supported on linux, not Windows, but will *try* to be supported soon.

The tool will work on any system that meets the minimum requirements. The tool will work better on systems that meet the recommended requirements. The tool will work best on systems that meet the best performance requirements. You can mix and match the requirements to get the best performance. For example, you can have a CPU that meets the best performance requirements and a GPU that meets the moderate requirements. The tool will work best on systems that meet the best performance requirements.

## A microphone is optional. You can use the `--stream` flag to stream audio from a HLS stream. See [Examples](#examples) for more information.
### You'll need some sort of software input source (or hardware source). See issue [#63](https://github.com/cyberofficial/Synthalingua/issues/63) for additional information.

## Installation
1. Download and install [Python 3.10.9](https://www.python.org/downloads/release/python-3109/).
     * Make sure to check the box that says "Add Python to PATH" when installing. If you don't check the box, you will have to manually add Python to your PATH. You can check this guide: [How to add Python to PATH](https://datatofish.com/add-python-to-windows-path/).
     * You can choose any python version that is 3.10.9 up to the latest version. The tool will *not* work on any python version that is 3.11 or higher. Must be 3.10.9+ not 3.11.x.
     * Make sure to grab the x64 bit version! This program is not compatible with x86. (32bit)
2. Download and install [Git](https://git-scm.com/downloads).
     * Using default settings is fine.
3. Download and install FFMPEG
     * Instructions: https://github.com/cyberofficial/Synthalingua/issues/2#issuecomment-1491098222
4. Download and install CUDA [Optional, but needs to be installed if using GPU]
     * https://developer.nvidia.com/cuda-downloads
5. Run setup script
     * **On Windows**: `setup.bat`
     * **On Linux**: `setup.bash`
          * Please ensure you have `gcc` installed and `portaudio19-dev` installed (or `portaudio-devel` for some machines`)
     * If you get an error saying "Setup.bat is not recognized as an internal or external command, operable program or batch file.", houston we have a problem. This will require you to fix your operating system.
6. Run the newly created batch file/bash script. You can edit that file to change the settings.
     * If you get an error saying it is "not recognized as an internal or external command, operable program or batch file.", make sure you have  installed and added to your PATH, and make sure you have git installed. If you have python and git installed and added to your PATH, then create a new issue on the repo and I will try to help you fix the issue.

## Usage 

This script uses argparse to accept command line arguments. The following options are available:
| Flag | Description |
| ---- | ----------- |
| `--ram` | Change the amount of RAM to use. Default is 4GB. Choices are "1GB", "2GB", "4GB", "6GB", "12GB-v2", "12GB-v3". |
| `--ramforce` | Use this flag to force the script to use desired VRAM. May cause the script to crash if there is not enough VRAM available. |
| `--fp16` | This allows for more accurate information being passed to the process. This will grant the AL the ability to process more information at the cost of speed. You will not see heavy impact on stronger hardware. Combine 12gb-v3 + fp16 Flags (Precision Mode on the GUI) for the ultimate experience. | 
| `--energy_threshold` | Set the energy level for microphone to detect. Default is 100. Choose from 1 to 1000; anything higher will be harder to trigger the audio detection. |
| `--mic_calibration_time` | How long to calibrate the mic for in seconds. To skip user input type 0 and time will be set to 5 seconds. |
| `--record_timeout` | Set the time in seconds for real-time recording. Default is 2 seconds. |
| `--phrase_timeout` | Set the time in seconds for empty space between recordings before considering it a new line in the transcription. Default is 1 second. |
| `--translate` | Translate the transcriptions to English. Enables translation. |
| `--transcribe` | Transcribe the audio to a set target language. Target Language flag is required. |
| `--target_language` | Select the language to translate to. Available choices are a list of languages in ISO 639-1 format, as well as their English names. |
| `--language` | Select the language to translate from. Available choices are a list of languages in ISO 639-1 format, as well as their English names. |
| ~~`--auto_model_swap`~~ | ~~Automatically swap the model based on the detected language. Enables automatic model swapping.~~ Removed, deprecated. |
| `--device` | Select the device to use for the model. Default is "cuda" if available. Available options are "cpu" and "cuda". When setting to CPU you can choose any RAM size as long as you have enough RAM. The CPU option is optimized for multi-threading, so if you have like 16 cores, 32 threads, you can see good results. |
| `--cuda_device` | Select the CUDA device to use for the model. Default is 0. |
| `--discord_webhook` | Set the Discord webhook to send the transcription to. |
| `--list_microphones` | List available microphones and exit. |
| `--set_microphone` | Set the default microphone to use. You can set the name or its ID number from the list. |
| `--microphone_enabled` | Enables microphone usage. Add `true` after the flag. |
| `--auto_language_lock` | Automatically lock the language based on the detected language after 5 detections. Enables automatic language locking. Will help reduce latency. Use this flag if you are using non-English and if you do not know the current spoken language. |
| `--model_dir` | Default location is "model" folder. You can use this argument to change location. |
| ~~`--use_finetune`~~ | ~~Use fine-tuned model. This will increase accuracy, but will also increase latency. Additional VRAM/RAM usage is required.~~ ⚠️ Fine Tune model is being retrained. Command flag is useless in current code. |
| `--no_log` | Makes it so only the last thing translated/transcribed is shown rather log style list. |
| `--updatebranch` | Check which branch from the repo to check for updates. Default is **master**, choices are **master** and **dev-testing** and **bleeding-under-work**. To turn off update checks use **disable**. **bleeding-under-work** is basically latest changes and can break at any time. |
| `--keep_temp` | Keeps audio files in the **out** folder. This will take up space over time though. |
| `--portnumber` | Set the port number for the web server. If no number is set then the web server will not start. |
| `--retry` | Retries translations and transcription if they fail. |
| `--about` | Shows about the app. |
| `--save_transcript` | Saves the transcript to a text file. |
| `--save_folder` | Set the folder to save the transcript to. |
| `--stream` | Stream audio from a HLS stream. |
| `--stream_language` | Language of the stream. Default is English. |
| `--stream_target_language` | Language to translate the stream to. Default is English. Needed for `--stream_transcribe` |
| `--stream_translate` | Translate the stream. |
| `--stream_transcribe` | Transcribe the stream to different language. Use `--stream_target_language` to change the output.  |
| `--stream_original_text` | Show the detected original text. |
| `--stream_chunks` | How many chunks to split the stream into. Default is 5 is recommended to be between 3 and 5. YouTube streams should be 1 or 2, twitch should be 5 to 10. The higher the number, the more accurate, but also the slower and delayed the stream translation and transcription will be. |
| `--cookies` | Cookies file name, just like twitch, youtube, twitchacc1, twitchacczed |
| `--makecaptions` | Set program to captions mode, requires file_input, file_output, file_output_name |
| `--file_input` | Location of file for the input to make captions for, almost all video/audio format supported (uses ffmpeg) |
| `--file_output` | Location of folder to export the captions |
| `--file_output_name` | File name to export as without any ext. |
| `--ignorelist` | Usage is "`--ignorelist "C:\quoted\path\to\wordlist.txt"`" |
| `--condition_on_previous_text` | Will help the model from repeating itself, but may slow up the process. |
| `--remote_hls_password_id` | Password ID for the webserver. Usually like 'id', or 'key'. Key is default for the program though, so when it asks for id/password, Synthalingua will be `key=000000` - `key`=`id` - `0000000`=`password` 16 chars long. |
| `--remote_hls_password` | Password for the hls webserver. |

# Things to note!
- When crafting your command line arguments, you need to make sure you adjust the energy threshold to your liking. The default is 100, but you can adjust it to your liking. The higher the number, the harder it is to trigger the audio detection. The lower the number, the easier it is to trigger the audio detection. I recommend you start with 100 and adjust it from there. I seen best results with 250-500.
- When using the discord webhook make sure the url is in quotes. Example: `--discord_webhook "https://discord.com/api/webhooks/1234567890/1234567890"`
- An active internet connection is required for initial usage. Over time you'll no longer need an internet connection. Changing RAM size will download certain models, once downloaded you'll no longer need internet.
- ~~The fine tuned model will automatically be downloaded from OneDrive via Direct Public link. In the event of failure~~ [ ⚠️ Finetune Model download is Disabled, Model is being retrained. ]
- When using more than one streaming option you may experience issues. This adds more jobs to the audio queue.

## Word Block List
With the flag `--ignorelist` you can now load a list of phrases or words to ignore in the api output and subtitle window. This list is already filled with common phrases the AI will think it heard. You can adjust this list as youu please or add more words or phrases to it.

## Cookies
Some streams may require cookies set, you'll need to save cookies as netscape format into the `cookies` folder as a .txt file. If a folder doesn't exist, create it.
You can save cookies using this https://cookie-editor.com/ or any other cookie editor, but it must be in netscape format.

Example usage `--cookies twitchacc1` **DO NOT** include the .txt file extension.

What ever you named the text file in the cookies folder, you'll need to use that name as the argument.

## Web Server
With the command flag `--port 4000`, you can use query parameters like `?showoriginal`, `?showtranslation`, and `?showtranscription` to show specific elements. If any other query parameter is used or no query parameters are specified, all elements will be shown by default. You can choose another number other than `4000` if you want. You can mix the query parameters to show specific elements, leave blank to show all elements.

For example:
- `http://localhost:4000?showoriginal` will show the `original` detected text.
- `http://localhost:4000?showtranslation` will show the `translated` text.
- `http://localhost:4000?showtranscription` will show the `transcribed` text.
- `http://localhost:4000/?showoriginal&showtranscription` will show the `original` and `transcribed` text.
- `http://localhost:4000` or `http://localhost:4000?otherparam=value` will show all elements by default.

## Examples
#### Please note, make sure you edit the livetranslation.bat/livetranslation.bash file to change the settings. If you do not, it will use the default settings.

This will create captions, with the 12GB-v3 option and save to downloads.

**PLEASE NOTE, CAPTIONS WILL ONLY BE IN ENGLISH (Model limitation) THOUGH YOU CAN ALWAYS USE OTHER PROGRAMS TO TRANSLATE INTO OTHER LANGUAGES**

`python transcribe_audio.py --ram 12GB-v3 --makecaptions --file_input="C:\Users\username\Downloads\430796208_935901281333537_8407224487814569343_n.mp4" --file_output="C:\Users\username\Downloads" --file_output_name="430796208_935901281333537_8407224487814569343_n" --language Japanese --device cuda` 

You have a 12gb GPU and want to stream the audio from a live stream https://www.twitch.tv/somestreamerhere and want to translate it to English. You can run the following command:

`python transcribe_audio.py --ram 12GB-v3 --stream_translate --stream_language Japanese --stream https://www.twitch.tv/somestreamerhere`

Stream Sources from YouTube and Twitch are supported. You can also use any other stream source that supports HLS/m3u8.


You have a GPU with 6GB of memory and you want to use the Japanese model. You also want to translate the transcription to English. You also want to send the transcription to a Discord channel. You also want to set the energy threshold to 300. You can run the following command:

`python transcribe_audio.py --ram 6gb --translate --language ja --discord_webhook "https://discord.com/api/webhooks/1234567890/1234567890" --energy_threshold 300`

When choosing ram, you can only choose 1gb, 2gb, 4gb, 6gb, 12GB-v2, 12GB-v3. There are no in-betweens.

You have a 12gb GPU and you want to translate to Spanish from English, you can run the following command for v3 replace v3 with v2 if you prefer the original:

`python transcribe_audio.py --ram 12GB-v3 --transcribe --target_language Spanish --language en`

Lets say you have multiple audio devices and you want to use the one that is not the default. You can run the following command:
`python transcribe_audio.py --list_microphones`
This command will list all audio devices and their index. You can then use the index to set the default audio device. For example, if you want to use the second audio device, you can run the following command:
`python transcribe_audio.py --set_microphone "Realtek Audio (2- High Definiti"` to set the device to listen to. *Please note the quotes around the device name. This is required to prevent errors. Some names may be cut off, copy exactly what is in the quotes of the listed devices.

Example lets say I have these devices:
```
Microphone with name "Microsoft Sound Mapper - Input" found, the device index is 1
Microphone with name "VoiceMeeter VAIO3 Output (VB-Au" found, the device index is 2
Microphone with name "Headset (B01)" found, the device index is 3
Microphone with name "Microphone (Realtek USB2.0 Audi" found, the device index is 4
Microphone with name "Microphone (NVIDIA Broadcast)" found, the device index is 5
```

I would put `python transcribe_audio.py --set_microphone "Microphone (Realtek USB2.0 Audi"` to set the device to listen to.
-or-
I would put `python transcribe_audio.py --set_microphone 4` to set the device to listen to.

## Troubleshooting

If you encounter any issues with the tool, here are some common problems and their solutions:

* Python is not recognized as an internal or external command, operable program or batch file.
    * Make sure you have Python installed and added to your PATH.
    * If you recently installed Python, try restarting your computer to refresh the PATH environment variable.
    * Check that you installed the correct version of Python required by the application. Some applications may require a specific version of Python.
    * If you are still having issues, try running the command prompt as an administrator and running the installation again. However, only do this as a last resort and with caution, as running scripts as an administrator can potentially cause issues with the system.
* I get an error saying "No module named 'transformers'".
    * Re-run the setup.bat file.
        * If issues persist, make sure you have Python installed and added to your PATH.
        * Make sure you have the `transformers` module installed by running `pip install transformers`.
        * If you have multiple versions of Python installed, make sure you are installing the module for the correct version by specifying the Python version when running the command, e.g. `python -m pip install transformers`.
        * If you are still having issues, create a new issue on the repository and the developer may be able to help you fix the issue.
* Git is not recognized as an internal or external command, operable program or batch file.
    * Make sure you have Git installed and added to your PATH.
    * If you recently installed Git, try restarting your computer to refresh the PATH environment variable.
    * If you are still having issues, try running the command prompt as an administrator and running the installation again. However, only do this as a last resort and with caution, as running scripts as an administrator can potentially cause issues with the system.
* CUDA is not recognized or available.
    * Make sure you have CUDA installed. You can get it from [here](https://developer.nvidia.com/cuda-downloads).
    * CUDA is only for NVIDIA GPUs. If you have an AMD GPU, you have to use the CPU model. ROCm is not supported at this time.
* [WinError 2] The system cannot find the file specified
    Try this fix: https://github.com/cyberofficial/Real-Time-Translation/issues/2#issuecomment-1491098222
* Translator can't pickup stream sound
    * Check out this discussion thread for a possible fix: [#12 Discussion](https://github.com/cyberofficial/Synthalingua/discussions/12)
* Error: Audio source must be entered before adjusting.
    * You need to make sure you have a microphone set up. See issue [#63](https://github.com/cyberofficial/Synthalingua/issues/63) for additional information.
* Error: "could not find a version that satisfies the requirement torch" (See Issue [#82](https://github.com/cyberofficial/Synthalingua/issues/82)) )
  * Please make sure you have python 64bit installed. If you have 32bit installed, you will need to uninstall it and install 64bit. You can grab it here for windows. Windows Direct: https://www.python.org/ftp/python/3.10.9/python-3.10.9-amd64.exe Main: https://www.python.org/downloads/release/python-3109/
* Error generating captions: Please make sure the file name is in english letters. If you still get an error, please make a bug report.

# Additional Information
* Models used are from OpenAI Whisper - [Whisper](https://github.com/openai/whisper)
    * Models were fine tuned using this [Documentation](https://huggingface.co/blog/fine-tune-whisper#load-whisperfeatureextractor)

# Video Demonstration
Command line arguments used. `--ram 6gb --record_timeout 2 --language ja --energy_threshold 500`
[<img src="https://i.imgur.com/sXTWr76.jpg" width="50%">](https://streamable.com/m9mhfr)

Command line arguments used. `--ram 12GB-v2 --record_timeout 5 --language id --energy_threshold 500`
[<img src="https://i.imgur.com/2WbWpH4.jpg" width="50%">](https://streamable.com/skuhoh)
