# Import necessary modules. Ensure 'modules.imports' contains all required imports.
from modules.imports import *
# Parse command-line arguments. Make sure 'parser_args.parse_arguments()' is properly set up in your project.
args = parser_args.parse_arguments()



# Function to detect language from an audio file.
def run_sub_gen(input_path: str, output_name: str = "", output_directory: str = "./"):
    model_type = parser_args.set_model_by_ram(args.ram, args.language)
    print("Loading Model")
    model = whisper.load_model(model_type, device=args.device, download_root=f"{args.model_dir}")

    print("Setting Path")
    print("Doing the work now...")
    print("This may take a while, sit back and get a coffee or something.")
    result = model.transcribe(input_path, fp16=args.fp16, language=args.language, task="translate", condition_on_previous_text=args.condition_on_previous_text)

    print("Setting writer Up")
    writer = get_writer("srt", str(output_directory))

    writer(result, output_name)
    print("Done...")
    return result, output_name

# Indicate that the subtitles generator module is loaded.
print("Subtitles Generator Module Loaded")
