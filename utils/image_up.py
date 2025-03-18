from fastapi import HTTPException, UploadFile, status
import os
import uuid
import shutil

STATIC_DIR = "static/images/"



async def save_image(file: UploadFile, subdir: str = "") -> str:
    if not file.filename:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not a avalid file")
    directory = os.path.join(STATIC_DIR, subdir)
    os.makedirs(directory, exist_ok=True)

    file_ext = file.filename.split(".")[-1]
    file_name = f"{uuid.uuid4()}.{file_ext}"
    file_path = os.path.join(directory, file_name)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return f"/{STATIC_DIR}{subdir}/{file_name}".replace("\\", "/")

async def delete_image(image_url: str):

    image_path = image_url.lstrip("/")
    if os.path.exists(image_path):
        os.remove(image_path)

        folder_path = os.path.dirname(image_path)
        if not os.listdir(folder_path): 
            shutil.rmtree(folder_path)
