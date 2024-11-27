from utils import (
    ensure_directory_exists,
    download_file,
    clean_text_for_filename,
    load_env_variable,
)
from google.cloud import texttospeech
from moviepy.editor import ImageSequenceClip, AudioFileClip
import openai
import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Retrieve API keys and credentials
OPENAI_API_KEY = load_env_variable("OPENAI_API_KEY")
GOOGLE_APPLICATION_CREDENTIALS = load_env_variable("GOOGLE_APPLICATION_CREDENTIALS")

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
    ensure_directory_exists(output_path)
    with open(output_path, "wb") as out:
        out.write(response.audio_content)
    return output_path


def generate_images(text):
    """Generates images from text using DALL·E."""
    response = openai.Image.create(
        prompt=text,
        n=5,
        size="1024x1024"
    )
    images = []
    for i, data in enumerate(response['data']):
        image_url = data['url']
        output_path = f"assets/images/image_{i}.png"
        download_file(image_url, output_path)
        images.append(output_path)
    return images


def create_video(images, audio_path, output_path="assets/video/output.mp4"):
    """Combines images and audio into a video."""
    clip = ImageSequenceClip(images, fps=1)
    audio = AudioFileClip(audio_path)
    clip = clip.set_audio(audio)
    ensure_directory_exists(output_path)
    clip.write_videofile(output_path, codec="libx264", audio_codec="aac")
    return output_path


if __name__ == "__main__":
    user_prompt = input("Enter a prompt: ")

    # Generate text
    generated_text = generate_text(user_prompt)
    print(f"Generated Text: {generated_text}")

    # Generate audio
    filename_safe_text = clean_text_for_filename(user_prompt)
    audio_path = generate_audio_google_tts(generated_text, f"assets/audio/{filename_safe_text}.mp3")

    # Generate images
    image_paths = generate_images(generated_text)

    # Create video
    video_path = create_video(image_paths, audio_path, f"assets/video/{filename_safe_text}.mp4")
    print(f"Video created at {video_path}")
