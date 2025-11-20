import os
import tempfile
from dotenv import load_dotenv
from app.utils.parsers import Parser
from app.utils.AI_client import get_llm_client

load_dotenv()


async def summarize_file(upload_file):
    suffix = "." + upload_file.filename.split('.')[-1]
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
        content = await upload_file.read()
        tmp.write(content)
        tmp_path = tmp.name

    try:
        text = Parser.from_path(tmp_path)
    finally:
        try:
            os.unlink(tmp_path)
        except Exception:
            pass

    return await summarize_text(text)


async def summarize_text(text: str) -> str:
    if not text or not text.strip():
        return "Пустой документ :("

    system_prompt = "Ты — помощник профессионального редактора текста. Сократи текст на 40%, сохранив основной смысл. В ответе дай лишь сокращённый текст."

    client = get_llm_client()
    result = await client.summarize(text, system_prompt=system_prompt)
    return result
