from fastapi import FastAPI, File, UploadFile, Request, Form
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.background import BackgroundTask

import os
import uuid
import zipfile
from pathlib import Path
from PIL import Image

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# Compactar imagem com controle de qualidade e redução percentual
def compress_image(input_path, output_path, quality=60, resize_percent=100):
    img = Image.open(input_path)

    # Reduz proporcionalmente com base no percentual
    if resize_percent < 100:
        new_width = int(img.width * resize_percent / 100)
        new_height = int(img.height * resize_percent / 100)
        img = img.resize((new_width, new_height), Image.LANCZOS)

    if img.mode in ("RGBA", "P"):
        img = img.convert("RGB")

    img.save(output_path, "JPEG", quality=quality, optimize=True)


def clear_upload_folder():
    for file in Path(UPLOAD_FOLDER).glob("*"):
        try:
            file.unlink()
        except Exception as e:
            print(f"Erro ao remover {file}: {e}")


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/upload/")
async def upload(
        files: list[UploadFile] = File(...),
        quality: int = Form(60),
        resize: int = Form(100)
):
    compressed_files = []

    for uploaded_file in files:
        original_name = uploaded_file.filename
        ext = os.path.splitext(original_name)[1].lower()
        unique_id = uuid.uuid4().hex[:8]

        input_path = os.path.join(UPLOAD_FOLDER, f"{unique_id}_original{ext}")
        output_path = os.path.join(UPLOAD_FOLDER, f"{unique_id}_compressed.jpg")

        with open(input_path, "wb") as f:
            f.write(await uploaded_file.read())

        compress_image(input_path, output_path, quality=quality, resize_percent=resize)

        compressed_files.append({
            "path": output_path,
            "original_name": f"{Path(original_name).stem}_compactado.jpg"
        })

    if len(compressed_files) == 1:
        file_info = compressed_files[0]
        return FileResponse(
            file_info["path"],
            media_type="image/jpeg",
            filename=file_info["original_name"],
            background=BackgroundTask(clear_upload_folder)
        )

    zip_name = os.path.join(UPLOAD_FOLDER, f"compressed_{uuid.uuid4().hex[:6]}.zip")
    with zipfile.ZipFile(zip_name, "w") as zipf:
        for file in compressed_files:
            zipf.write(file["path"], arcname=file["original_name"])

    return FileResponse(
        zip_name,
        media_type="application/zip",
        filename=os.path.basename(zip_name),
        background=BackgroundTask(clear_upload_folder)
    )
