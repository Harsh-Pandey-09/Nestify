import os
from fastapi import UploadFile, HTTPException, status

from app.utils.constants import ALLOWED_IMAGE_EXTENSIONS, MAX_IMAGE_SIZE_MB


def validate_image_file(file: UploadFile):
    ext = os.path.splitext(file.filename or "")[1].lower()
    if ext not in ALLOWED_IMAGE_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file type '{ext}'. Allowed: {sorted(ALLOWED_IMAGE_EXTENSIONS)}",
        )
    return ext
