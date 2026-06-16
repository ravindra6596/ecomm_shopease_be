import os
import uuid
import shutil
from typing import List, Tuple
from fastapi import UploadFile
from app.config.config import settings

TEMP_DIR = os.path.join("media", "temp")
FINAL_DIR = os.path.join("media", settings.UPLOAD_DIR)
BASE_URL = settings.BASE_URL


def ensure_dirs(upload_dir=None):
    os.makedirs(TEMP_DIR, exist_ok=True)
    if upload_dir:
        final_dir = os.path.join("media", upload_dir)
    else:
        final_dir = FINAL_DIR
    os.makedirs(final_dir, exist_ok=True)


def generate_filename(filename: str) -> str:
    ext = filename.split(".")[-1]
    return f"{uuid.uuid4()}.{ext}"


def save_temp_file(file: UploadFile) -> Tuple[str, str]:
    ensure_dirs()

    filename = generate_filename(file.filename)
    temp_path = os.path.join(TEMP_DIR, filename)

    with open(temp_path, "wb") as f:
        f.write(file.file.read())

    return temp_path, filename


def move_to_final(temp_path: str, filename: str, upload_dir=None) -> str:
    ensure_dirs(upload_dir)

    if upload_dir:
        final_dir = os.path.join("media", upload_dir)
    else:
        final_dir = FINAL_DIR

    final_path = os.path.join(final_dir, filename)
    shutil.move(temp_path, final_path)

    return final_path
#  Delete single file (by full path OR URL)
def delete_file(path_or_url: str):
    try:
        # convert URL → local path
        if path_or_url.startswith(settings.BASE_URL):
            path = path_or_url.replace(settings.BASE_URL + "/", "")
        else:
            path = path_or_url

        if os.path.exists(path):
            os.remove(path)
    except Exception:
        pass


# Delete multiple files
def delete_multiple_files(paths: List[str]):
    for path in paths:
        delete_file(path)


def cleanup_temp_files(temp_files: List[Tuple[str, str]]):
    for temp_path, _ in temp_files:
        if os.path.exists(temp_path):
            os.remove(temp_path)