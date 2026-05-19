from pathlib import Path
from uuid import uuid4

from fastapi import UploadFile

UPLOAD_DIR = Path(__file__).resolve().parents[2] / "uploads"


async def save_upload(file: UploadFile) -> Path:
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    suffix = Path(file.filename or "").suffix.lower() or ".audio"
    target_path = UPLOAD_DIR / f"{uuid4().hex}{suffix}"

    with target_path.open("wb") as output:
        while chunk := await file.read(1024 * 1024):
            output.write(chunk)

    return target_path
