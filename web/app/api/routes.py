import os
import json
from fastapi import APIRouter, UploadFile, File, Form, Request
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates
from app.services.summarizer import summarize_file, summarize_text

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "app/templates"))

@router.post("/api/summarize")
async def summarize(request: Request,
                    document: UploadFile | None = File(None),
                    text: str | None = Form(None)):
    if not document and not text:
        return JSONResponse({"error": "Необходимо передать файл или текст"}, status_code=400)
    if document:
        result_text = await summarize_file(document)
    else:
        result_text = await summarize_text(text)

    return JSONResponse({"summarized_text": result_text})
