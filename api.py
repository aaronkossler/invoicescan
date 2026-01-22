from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
from pathlib import Path
import tempfile
import shutil
from backend import Backend, BackendType

app = FastAPI(title="Invoice Scanner API")
FRONTEND_PATH = Path(__file__).parent / "frontend"

BACKEND_URL = "http://localhost:8080/v1"


@app.post("/process")
async def process_invoice(file: UploadFile = File(...)):
    """Process an invoice image and extract properties."""
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")

    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
        shutil.copyfileobj(file.file, tmp)
        tmp_path = tmp.name

    try:
        backend = Backend(type=BackendType.LLAMA, base_url=BACKEND_URL)
        result = backend.process_invoice(tmp_path)

        if result is None:
            return {"error": "No invoice detected in image"}

        import json
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
