import uuid
import os


def generate_unique_filename(extension: str) -> str:
    return f"{uuid.uuid4().hex}{extension}"


def ensure_dir(path: str):
    os.makedirs(path, exist_ok=True)
