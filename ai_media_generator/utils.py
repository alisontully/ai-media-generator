import os
import requests


def ensure_directory_exists(file_path):
    """
    Ensures that the directory for the given file path exists. Creates it if it doesn't.

    Args:
        file_path (str): The path to the file or directory.
    """
    os.makedirs(os.path.dirname(file_path), exist_ok=True)


def download_file(url, output_path):
    """
    Downloads a file from the given URL and saves it to the specified output path.

    Args:
        url (str): The URL to download the file from.
        output_path (str): The path to save the downloaded file.

    Returns:
        str: The output path where the file was saved.
    """
    ensure_directory_exists(output_path)
    response = requests.get(url, stream=True)
    if response.status_code == 200:
        with open(output_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        return output_path
    else:
        raise Exception(f"Failed to download file from {url}. Status code: {response.status_code}")


def clean_text_for_filename(text, max_length=50):
    """
    Cleans a string to make it safe to use as a filename.

    Args:
        text (str): The string to clean.
        max_length (int): The maximum length of the filename.

    Returns:
        str: A cleaned, safe filename.
    """
    import re
    filename = re.sub(r"[^\w\s-]", "", text)  # Remove invalid characters
    filename = re.sub(r"[\s]+", "_", filename)  # Replace spaces with underscores
    return filename[:max_length].strip("_")


def load_env_variable(key, default=None):
    """
    Loads an environment variable and returns its value or a default if not found.

    Args:
        key (str): The environment variable key.
        default (str): The default value if the environment variable is not found.

    Returns:
        str: The value of the environment variable or the default.
    """
    return os.getenv(key, default)


def format_size(size_in_bytes):
    """
    Formats a size in bytes into a human-readable string (e.g., "2.5 MB").

    Args:
        size_in_bytes (int): Size in bytes.

    Returns:
        str: Formatted size string.
    """
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if size_in_bytes < 1024:
            return f"{size_in_bytes:.2f} {unit}"
        size_in_bytes /= 1024
