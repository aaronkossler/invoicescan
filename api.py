import json
import tempfile
import shutil
from os import getenv
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from backend import Backend, BackendType

load_dotenv()

app = FastAPI(title="Invoice Scanner API")
FRONTEND_PATH = Path(__file__).parent / "frontend"


@app.post("/process")
async def process_invoice(file: UploadFile = File(...)):
    """Process an invoice image and extract properties."""
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")

    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
        shutil.copyfileobj(file.file, tmp)
        tmp_path = tmp.name

    try:
        backend_url = getenv("LLAMA_SERVER_URL", "http://localhost:8080/v1")
        backend = Backend(type=BackendType.LLAMA, base_url=backend_url)
        result = backend.process_invoice(tmp_path)

        if result is None:
            return {"error": "No invoice detected in image"}

        data = json.loads(result)
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        Path(tmp_path).unlink(missing_ok=True)


@app.get("/")
async def serve_frontend():
    """Serve the main frontend page."""
    return FileResponse(FRONTEND_PATH / "index.html")


@app.get("/{filename}")
async def serve_static(filename: str):
    """Serve static files (CSS, JS)."""
    file_path = FRONTEND_PATH / filename
    if file_path.exists() and file_path.is_file():
        return FileResponse(file_path)
    raise HTTPException(status_code=404, detail="File not found")


def main():
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    main()
