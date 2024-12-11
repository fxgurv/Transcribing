# main.py
from app import SubtitlesGenerator
import os

def find_audio_file(directory):
    """Find the first audio file in the directory"""
    audio_extensions = ('.mp3', '.wav', '.m4a', '.aac', '.ogg', '.flac', '.avi')
    for file in os.listdir(directory):
        if file.lower().endswith(audio_extensions):
            return os.path.join(directory, file)
    return None

def find_image_files(directory):
    """Find all image files in the directory"""
    image_extensions = ('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp')
    images = []
    for file in os.listdir(directory):
        if file.lower().endswith(image_extensions):
            images.append(os.path.join(directory, file))
    return sorted(images)  # Sort to ensure consistent order

def main():
    # Get the root directory and .mp directory
    ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    MP_DIR = os.path.join(ROOT_DIR, ".mp")

    # Find audio and image files
    tts_path = find_audio_file(MP_DIR)
    images = find_image_files(MP_DIR)

    # Validate inputs
    if not tts_path:
        print("Error: No audio file found in .mp directory!")
        return
    
    if not images:
        print("Error: No image files found in .mp directory!")
        return

    print(f"Found audio file: {os.path.basename(tts_path)}")
    print(f"Found {len(images)} images")

    try:
        # Create SubtitlesGenerator instance
        generator = SubtitlesGenerator(
            tts_path=tts_path,
            images=images
        )

        # Generate the final video
        output_path = generator.combine()

        if output_path:
            print(f"Video successfully generated at: {output_path}")
        else:
            print("Failed to generate video")

    except Exception as e:
        print(f"Error occurred: {str(e)}")

if __name__ == "__main__":
    main()
