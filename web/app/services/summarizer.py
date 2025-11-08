import os
import tempfile
import requests
from openai import OpenAI
from dotenv import load_dotenv
from app.utils.parsers import extract_text_from_file


load_dotenv()
api_key = os.getenv("OPENROUTER_API_KEY")
api_url = os.getenv("OPENROUTER_API_URL")
api_model = os.getenv("OPENROUTER_MODEL")


async def summarize_file(upload_file):
    suffix = "." + upload_file.filename.split('.')[-1]    # тут определяю расширение файла
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
        content = await upload_file.read()
        tmp.write(content)
        tmp_path = tmp.name

    text = extract_text_from_file(tmp_path)
    os.unlink(tmp_path)
    return await summarize_text(text)

async def summarize_text(text: str):
    if not text.strip():
        return "Пустой документ :("

    prompt = f"""Сократи текст, сохранив основной смысл.
            В ответе дай лишь сокращённый текст. \n\n Текст: \n {text}"""

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost:8000",
        "X-Title": "FastAPI LLM Client"
    }

    payload = {
        "model": f"{api_model}",
        "messages": [
            {"role": "system", "content": "Ты — профессиональный редактор текста."},
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 4000
    }

    response = requests.post(api_url, headers=headers, json=payload)
    data = response.json()
    if "error" in data:
        return {"error": data["error"]["message"]}
    
    return data["choices"][0]["message"]["content"]
