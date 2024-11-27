
# AI Media Generator

AI Media Generator is a Python application that generates multimedia content based on user prompts. It uses the following capabilities:
- **OpenAI GPT** for text generation.
- **Google Cloud Text-to-Speech** for audio narration.
- **DALL·E** for image generation.
- **MoviePy** for combining images and audio into a video.

## Features
1. **Text Generation**: Generate stories or scripts based on user prompts.
2. **Scene Division**: Automatically splits generated text into scenes.
3. **Image Creation**: Generates one image per scene using DALL·E.
4. **Audio Narration**: Converts the full story into audio using Google Text-to-Speech.
5. **Video Creation**: Combines images and audio into a cohesive video.

---

## Installation

### Prerequisites
- Python 3.10+
- Google Cloud account with Text-to-Speech API enabled.
- OpenAI API key for GPT and DALL·E access.
- FFmpeg installed (for MoviePy and Pydub).

### Clone the Repository
```bash
git clone https://github.com/alisontully/ai-media-generator.git
cd ai-media-generator
```

### Set Up the Environment
1. Install dependencies:
    ```bash
    poetry install
    ```
2. Add your environment variables in a `.env` file:
    ```
    OPENAI_API_KEY=your_openai_api_key
    GOOGLE_APPLICATION_CREDENTIALS=/path/to/your-google-credentials.json
    ```

3. Install FFmpeg:
    - **macOS**: `brew install ffmpeg`
    - **Linux**: `sudo apt install ffmpeg`
    - **Windows**: [Download FFmpeg](https://ffmpeg.org/download.html)

---

## Usage
Run the main script:
```bash
python -m ai_media_generator.main
```

1. Enter a story prompt when prompted.
2. The application will:
   - Generate text based on your prompt.
   - Split the text into scenes.
   - Generate images for each scene.
   - Create audio narration for the full text.
   - Combine images and audio into a video.
3. The video will be saved in `assets/video/output.mp4`.

---

## Directory Structure
```
ai-media-generator/
├── ai_media_generator/
│   ├── main.py                # Main script
│   ├── utils.py               # Utility functions
├── assets/
│   ├── audio/                 # Generated audio files
│   ├── images/                # Generated images
│   ├── video/                 # Generated videos
├── .env                       # Environment variables (not tracked by Git)
├── README.md                  # Project README
```

---

## Troubleshooting
1. **Error: `FileNotFoundError: 'ffprobe'`**  
   Ensure FFmpeg is installed and available in your system PATH.

2. **OpenAI Errors**  
   - Check your OpenAI API key and ensure your account has sufficient credits.
   - Verify that you have access to the required models (e.g., GPT-4 and DALL·E).

3. **Google TTS Errors**  
   - Ensure your Google Cloud credentials file is correct and the API is enabled.

---

## Contributing
1. Fork the repository.
2. Create a feature branch (`git checkout -b feature-branch`).
3. Commit your changes (`git commit -m "Add feature"`).
4. Push to your fork (`git push origin feature-branch`).
5. Open a pull request.

---

## License
This project is licensed under the MIT License.

---

## Acknowledgements
- [OpenAI GPT](https://openai.com/)
- [Google Cloud Text-to-Speech](https://cloud.google.com/text-to-speech)
- [DALL·E](https://openai.com/dall-e/)
- [MoviePy](https://zulko.github.io/moviepy/)
- [Pydub](https://github.com/jiaaro/pydub)
