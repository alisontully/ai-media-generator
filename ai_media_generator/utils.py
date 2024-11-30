import os
import re
from typing import Optional

import requests  # type: ignore


def ensure_directory_exists(file_path: str) -> None:
    """Ensures that the directory for the given file path exists."""
    os.makedirs(os.path.dirname(file_path), exist_ok=True)


def download_file(url: str, output_path: str, timeout: int = 10) -> str:
    """
    Downloads a file from the given URL and saves it to the specified output path.

    Args:
        url (str): The URL to download the file from.
        output_path (str): The path to save the downloaded file.
        timeout (int): The timeout for the request in seconds (default: 10).

    Returns:
        str: The output path where the file was saved.

    Raises:
        RuntimeError: If the download fails due to an HTTP error.
    """
    ensure_directory_exists(output_path)
    response = requests.get(url, stream=True, timeout=timeout)
    if response.status_code == 200:
        with open(output_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        return output_path
    raise RuntimeError(f"Failed to download file from {url}. Status code: {response.status_code}")


def clean_text_for_filename(text: str, max_length: int = 50) -> str:
    """
    Cleans a string to make it safe for use as a filename.

    Args:
        text (str): The input string to be cleaned.
        max_length (int): The maximum length for the filename (default is 50).

    Returns:
        str: A cleaned and safe filename string.
    """
    filename = re.sub(r"[^\w\s-]", "", text)  # Remove invalid characters
    filename = re.sub(r"[\s]+", "_", filename)  # Replace spaces with underscores
    return filename[:max_length].strip("_")  # Trim to max length and remove trailing underscores


def load_env_variable(key: str, default: Optional[str] = None) -> Optional[str]:
    """Loads an environment variable or returns a default value."""
    return os.getenv(key, default)
