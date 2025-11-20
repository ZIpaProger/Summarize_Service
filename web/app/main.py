
import os
from fastapi import FastAPI, Request, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from app.api.routes import router as api_router
from app.services.summarizer import summarize_file


app = FastAPI(
    title="Summarization Service",
    description="Сервис сокращения текста документов с использованием LLM",
    version="1.0.0"
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

app.include_router(api_router)

templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "app/templates"))

@app.get("/", response_class=HTMLResponse)
async def upload_form(request: Request):
    return templates.TemplateResponse("upload.html", {"request": request})

@app.post("/summarize", response_class=JSONResponse)
async def summarize_view(request: Request,
                         document: UploadFile = File(...)):
    summarized_text = await summarize_file(document)

    return JSONResponse({"summarized_text": summarized_text})
    # return templates.TemplateResponse(
    #     "response.html",
    #     {
    #         "request": request,
    #         "summarized_text": summarized_text
    #     }
    # )

