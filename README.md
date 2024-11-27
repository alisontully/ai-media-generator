# AI Media Generator

A Python-based project that generates videos using AI. The workflow includes:
1. Generating text using ChatGPT.
2. Converting the text to audio using Aidocmaker's AI Voice Generator.
3. Creating images based on the text using DALL·E.
4. Compiling everything into a video.

---

## Features

- **Text Generation**: Uses OpenAI's ChatGPT API for generating text from a prompt.
- **Audio Generation**: Converts the generated text to high-quality speech using Aidocmaker's AI Voice Generator.
- **Image Generation**: Generates images based on the text using OpenAI's DALL·E API.
- **Video Creation**: Combines the generated audio and images into a video.

---

## Prerequisites

- **Python**: Version 3.10 or higher.
- **Conda**: For environment management.
- **Poetry**: For dependency management (installed automatically by the setup script).

---

## Setup Instructions

### 1. Clone the Repository
```bash
git clone https://github.com/alisontully/ai-media-generator.git
cd ai-media-generator
```

### 2. Set Environment Variables
Before running the setup, make sure to set the following environment variables:
- `ENV_NAME`: Name of the Conda environment (e.g., `ai-media-env`).
- `PYTHON_VERSION`: Python version to use (e.g., `3.10`).
- `PROJECT_NAME` (optional): Project name (default: `ai-media-generator`).

Copy `.env.example` to `.env` and fill in the required values.

### 3. Run the Setup Script
Run the `setup.sh` script to create the environment, install dependencies, and configure the project:
```bash
ENV_NAME=ai-media-env PYTHON_VERSION=3.10 PROJECT_NAME=ai-media-generator ./setup.sh
```

The script performs the following steps:
- Creates a Conda environment with the specified Python version.
- Installs Poetry in the environment.
- Configures the project name and Python version in `pyproject.toml`.
- Installs dependencies and locks them.
- Installs pre-commit hooks.
- Installs the project as a Python package.

### 4. Activate the Environment
After setup, activate the Conda environment:
```bash
conda activate ai-media-env
```

---

## Running the Project

To generate media, run the main script:
```bash
python ai_media_generator/main.py
```

---

## Project Structure

```
ai-media-generator/
│
├── ai_media_generator/      # Main package folder
│   ├── __init__.py
│   ├── main.py              # Main script
│   ├── api_keys.py          # API keys (use environment variables in production)
│   └── utils.py             # Utility functions (optional)
│
├── assets/                  # Directory for generated media
│   ├── audio/
│   ├── images/
│   └── video/
│
├── tests/                   # Test cases
│   ├── __init__.py
│   └── test_main.py
│
├── setup.sh                 # Environment setup script
├── pyproject.toml           # Poetry configuration file
├── requirements.txt         # Exported dependencies for compatibility
├── README.md                # Documentation
└── .gitignore               # Git ignore file
```

---

## Contributing

1. Fork the repository.
2. Create a feature branch:
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. Commit your changes and push to your fork.
4. Submit a pull request.

---

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.

---

