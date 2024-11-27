from ai_media_generator.utils import download_file, ensure_directory_exists, clean_text_for_filename
from dotenv import load_dotenv
import os
from google.cloud import texttospeech
from moviepy.editor import VideoFileClip, concatenate_videoclips, AudioFileClip, ImageClip
from pydub import AudioSegment
import openai

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

def generate_text(prompt):
    """Generates text using ChatGPT."""
    response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
    )
    return response['choices'][0]['message']['content']

def generate_audio_google_tts(text, output_path="assets/audio/output.mp3"):
    """Generates audio from text using Google Cloud Text-to-Speech."""
    client = texttospeech.TextToSpeechClient()

    # Set the text input
    synthesis_input = texttospeech.SynthesisInput(text=text)

    # Select the voice and audio configuration
    voice = texttospeech.VoiceSelectionParams(
        language_code="en-US",
        ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL
    )
    audio_config = texttospeech.AudioConfig(audio_encoding=texttospeech.AudioEncoding.MP3)

    # Perform the text-to-speech request
    response = client.synthesize_speech(
        input=synthesis_input, voice=voice, audio_config=audio_config
    )

    # Save the audio file
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "wb") as out:
        out.write(response.audio_content)
    return output_path

def split_audio_by_scenes(audio_path, scene_durations, output_dir="assets/audio/scenes"):
    """Splits the narration audio into smaller files for each scene."""
    audio = AudioSegment.from_file(audio_path)
    os.makedirs(output_dir, exist_ok=True)

    start = 0
    scene_audio_paths = []
    for idx, duration in enumerate(scene_durations):
        end = start + (duration * 1000)  # Convert seconds to milliseconds
        scene_audio = audio[start:end]
        output_path = os.path.join(output_dir, f"scene_{idx + 1}.mp3")
        scene_audio.export(output_path, format="mp3")
        scene_audio_paths.append(output_path)
        start = end

    return scene_audio_paths

def create_video_for_scene(image, audio_path, scene_index, output_dir="assets/video/scenes", fps=24):
    """
    Creates a video for a single scene.

    Args:
        image (str): Path to the image file for the scene.
        audio_path (str): Path to the audio file snippet for the scene.
        scene_index (int): Index of the scene.
        output_dir (str): Directory to save the scene videos.
        fps (int): Frames per second for the video.

    Returns:
        str: Path to the created scene video.
    """
    from moviepy.video.VideoClip import ImageClip

    # Ensure the output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Load the audio and calculate its duration
    audio_clip = AudioFileClip(audio_path)
    duration = audio_clip.duration

    # Create a video clip from the image
    video_clip = ImageClip(image).set_duration(duration).set_audio(audio_clip)
    video_clip.fps = fps  # Explicitly set fps for the clip

    # Save the video for the scene
    output_path = os.path.join(output_dir, f"scene_{scene_index}.mp4")
    video_clip.write_videofile(output_path, codec="libx264", audio_codec="aac", fps=fps)

    return output_path


def combine_scene_videos(scene_videos, output_path="assets/video/output.mp4"):
    """Combines all scene videos into a single video."""
    clips = [VideoFileClip(video) for video in scene_videos]
    final_video = concatenate_videoclips(clips, method="compose")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    final_video.write_videofile(output_path, codec="libx264", audio_codec="aac")
    return output_path

if __name__ == "__main__":
    user_prompt = input("Enter a prompt: ")

    # Modify the prompt to instruct GPT to generate text divided into scenes
    modified_prompt = (
        f"Using the following input: '{user_prompt}', write a story and divide it into clear scenes. "
        "Each scene should begin with a title in the format 'Scene [number]:' followed by a concise visual description of the key moment in the scene. Focus on vivid, imagery-driven descriptions that can inspire illustrations or visuals."
    )




    # Generate text based on the modified prompt
    generated_text = generate_text(modified_prompt)
    print(f"Generated Text:\n{generated_text}")

    # Extract scenes from the generated text
    print("Generating images for each scene...")
    scenes = [
        line.strip()
        for line in generated_text.split('\n')
        if line.strip().startswith("Scene") or line.strip().startswith("**Scene")
    ]
    image_paths = []
    for idx, scene in enumerate(scenes, start=1):
        try:
            response = openai.Image.create(
                prompt=scene,
                n=1,
                size="1024x1024"
            )
            image_url = response['data'][0]['url']
            output_path = f"assets/images/scene_{idx}.png"
            download_file(image_url, output_path)
            image_paths.append(output_path)
        except openai.error.OpenAIError as e:
            print(f"Error generating image for {scene}: {e}")

    print(f"Generated {len(image_paths)} images for the scenes.")

    # Generate audio for the full story
    print("Generating audio for the story...")
    audio_path = generate_audio_google_tts(generated_text)

    # Estimate scene durations equally for now
    scene_durations = [len(AudioSegment.from_file(audio_path)) // 1000 // len(scenes)] * len(scenes)

    # Split audio for scenes
    scene_audio_paths = split_audio_by_scenes(audio_path, scene_durations)

    # Create individual videos for each scene
    print("Creating individual videos for each scene...")
    scene_video_paths = []
    for idx, (image, audio) in enumerate(zip(image_paths, scene_audio_paths), start=1):
        scene_video_path = create_video_for_scene(image, audio, idx)
        scene_video_paths.append(scene_video_path)

    # Combine all scene videos into a final video
    print("Combining all scene videos into a final video...")
    final_video_path = combine_scene_videos(scene_video_paths)
    print(f"Final video created at {final_video_path}")
