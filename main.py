import os

import openai
from dotenv import load_dotenv
from google.cloud import texttospeech
from moviepy.editor import (
    AudioFileClip,
    ImageClip,
    VideoFileClip,
    concatenate_videoclips,
)
from pydub import AudioSegment

from ai_media_generator.utils import download_file, ensure_directory_exists

# Load environment variables
load_dotenv()

# Retrieve API keys and credentials
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GOOGLE_APPLICATION_CREDENTIALS = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY not found. Ensure it's set in the .env file.")
if not GOOGLE_APPLICATION_CREDENTIALS:
    raise ValueError("GOOGLE_APPLICATION_CREDENTIALS not found. Ensure it's set in the .env file.")

# Set Google Application Credentials
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = GOOGLE_APPLICATION_CREDENTIALS

# Configure OpenAI API
openai.api_key = OPENAI_API_KEY


def generate_text(prompt: str) -> str:
    """
    Generates text using ChatGPT.

    Args:
        prompt (str): The user prompt to generate text for.

    Returns:
        str: The generated text from ChatGPT.
    """
    ai_response = openai.ChatCompletion.create(  # Renamed to `ai_response`
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
    )
    return ai_response["choices"][0]["message"]["content"]


def generate_audio_google_tts(text: str, audio_output_path: str = "assets/audio/output.mp3") -> str:
    """
    Generates audio from text using Google Cloud Text-to-Speech.

    Args:
        text (str): The input text to convert to speech.
        audio_output_path (str): The file path to save the generated audio (default: "assets/audio/output.mp3").

    Returns:
        str: The path to the generated audio file.
    """
    client = texttospeech.TextToSpeechClient()

    synthesis_input = texttospeech.SynthesisInput(text=text)
    voice = texttospeech.VoiceSelectionParams(language_code="en-US", ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL)
    audio_config = texttospeech.AudioConfig(audio_encoding=texttospeech.AudioEncoding.MP3)

    tts_response = client.synthesize_speech(input=synthesis_input, voice=voice, audio_config=audio_config)

    ensure_directory_exists(audio_output_path)
    with open(audio_output_path, "wb") as out_file:  # Renamed to `out_file` for clarity
        out_file.write(tts_response.audio_content)
    return audio_output_path


def split_audio_by_scenes(
    input_audio_path: str, scene_lengths: list[int], output_dir: str = "assets/audio/scenes"
) -> list[str]:
    """
    Splits the narration audio into smaller files for each scene.

    Args:
        input_audio_path (str): The path to the input audio file.
        scene_lengths (list[int]): A list of scene durations in seconds.
        output_dir (str): Directory to save the split audio files (default: "assets/audio/scenes").

    Returns:
        list[str]: A list of paths to the split audio files.
    """
    # Load the audio file
    audio = AudioSegment.from_file(input_audio_path)
    os.makedirs(output_dir, exist_ok=True)

    start_time = 0  # Track the start of each scene
    split_audio_paths = []  # Store paths to the split audio files

    for scene_index, duration_seconds in enumerate(scene_lengths):
        end_time = start_time + (duration_seconds * 1000)  # Convert to milliseconds
        scene_audio = audio[start_time:end_time]
        scene_output_path = os.path.join(output_dir, f"scene_{scene_index + 1}.mp3")
        scene_audio.export(scene_output_path, format="mp3")
        split_audio_paths.append(scene_output_path)
        start_time = end_time

    return split_audio_paths


def create_video_for_scene(
    image: str, scene_audio_path: str, scene_index: int, output_dir: str = "assets/video/scenes", fps: int = 24
) -> str:
    """
    Creates a video for a single scene.

    Args:
        image (str): Path to the image file for the scene.
        scene_audio_path (str): Path to the audio file snippet for the scene.
        scene_index (int): Index of the scene.
        output_dir (str): Directory to save the scene videos.
        fps (int): Frames per second for the video.

    Returns:
        str: Path to the created scene video.
    """
    ensure_directory_exists(output_dir)

    # Load audio and set the duration
    audio_clip = AudioFileClip(scene_audio_path)
    duration = audio_clip.duration

    # Create video with image and audio
    video_clip = ImageClip(image).set_duration(duration).set_audio(audio_clip)
    video_clip.fps = fps

    # Define output path
    scene_video_output = os.path.join(output_dir, f"scene_{scene_index}.mp4")
    video_clip.write_videofile(scene_video_output, codec="libx264", audio_codec="aac", fps=fps)

    return scene_video_output


def combine_scene_videos(scene_videos: list[str], output_video_path: str = "assets/video/output.mp4") -> str:
    """
    Combines all scene videos into a single video.

    Args:
        scene_videos (list[str]): List of paths to individual scene video files.
        output_video_path (str): Path to save the combined video (default: "assets/video/output.mp4").

    Returns:
        str: Path to the final combined video.
    """
    clips = [VideoFileClip(video) for video in scene_videos]
    final_video = concatenate_videoclips(clips, method="compose")
    ensure_directory_exists(output_video_path)
    final_video.write_videofile(output_video_path, codec="libx264", audio_codec="aac")
    return output_video_path


if __name__ == "__main__":
    user_prompt = input("Enter a prompt: ")

    modified_prompt = (
        f"Using the following input: '{user_prompt}', write a story and divide it into clear scenes. "
        "Each scene should begin with a title in the format 'Scene [number]:' "
        "followed by a concise visual description of the key moment in the scene. "
        "Focus on vivid, imagery-driven descriptions that can inspire illustrations or visuals."
    )

    generated_text = generate_text(modified_prompt)
    print(f"Generated Text:\n{generated_text}")

    print("Generating images for each scene...")
    scenes = [
        line.strip()
        for line in generated_text.split("\n")
        if line.strip().startswith("Scene") or line.strip().startswith("**Scene")
    ]
    image_paths = []
    for idx, scene in enumerate(scenes, start=1):
        try:
            response = openai.Image.create(prompt=scene, n=1, size="1024x1024")
            image_url = response["data"][0]["url"]
            output_path = f"assets/images/scene_{idx}.png"
            download_file(image_url, output_path)
            image_paths.append(output_path)
        except openai.error.OpenAIError as e:
            print(f"Error generating image for {scene}: {e}")

    print(f"Generated {len(image_paths)} images for the scenes.")
    audio_path = generate_audio_google_tts(generated_text)
    scene_durations = [len(AudioSegment.from_file(audio_path)) // 1000 // len(scenes)] * len(scenes)
    scene_audio_paths = split_audio_by_scenes(audio_path, scene_durations)

    print("Creating individual videos for each scene...")
    scene_video_paths = [
        create_video_for_scene(image, audio, idx)
        for idx, (image, audio) in enumerate(zip(image_paths, scene_audio_paths), start=1)
    ]

    print("Combining all scene videos into a final video...")
    final_video_path = combine_scene_videos(scene_video_paths)
    print(f"Final video created at {final_video_path}")
