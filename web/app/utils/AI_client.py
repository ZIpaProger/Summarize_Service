import os
import asyncio
from typing import Optional

import requests
from dotenv import load_dotenv

load_dotenv()


class LLMClient:
	"""Класс-клиент для взаимодействия с LLM провайдерами."""

	async def summarize(self,
					 text: str,
					 system_prompt: Optional[str] = None) -> str:
		raise NotImplementedError


class OpenRouterClient(LLMClient):
	def __init__(self, api_key: Optional[str] = None, api_url: Optional[str] = None, model: Optional[str] = None):
		self.api_key = api_key or os.getenv("OPENROUTER_API_KEY")
		self.api_url = api_url or os.getenv("OPENROUTER_API_URL")
		self.model = model or os.getenv("OPENROUTER_MODEL")

	async def summarize(self,
					 text: str,
					 system_prompt: Optional[str] = None) -> str:
		if not self.api_key or not self.api_url or not self.model:
			raise RuntimeError("OpenRouter configuration не обнаружила (OPENROUTER_API_KEY/URL/MODEL)")

		prompt = text
		if system_prompt:
			messages = [
				{"role": "system", "content": system_prompt},
				{"role": "user", "content": prompt}
			]
		else:
			messages = [{"role": "user", "content": prompt}]

		headers = {
			"Authorization": f"Bearer {self.api_key}",
			"Content-Type": "application/json"
		}

		payload = {
			"model": self.model,
			"messages": messages,
		}

		def _post():
			resp = requests.post(self.api_url, headers=headers, json=payload, timeout=60)
			resp.raise_for_status()
			return resp.json()

		data = await asyncio.to_thread(_post)
		# желаемый ответ: choices[0].message.content
		if "error" in data:
			raise RuntimeError(data["error"])
		try:
			return data["choices"][0]["message"]["content"]
		except Exception as e:
			raise RuntimeError("Неверный формат ответа OpenRouter") from e


class OpenAIClient(LLMClient):
	def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
		self.api_key = api_key or os.getenv("OPENAI_API_KEY")
		self.model = model or os.getenv("OPENAI_MODEL")
		try:
			from openai import OpenAI
			self._client = OpenAI(api_key=self.api_key)
		except Exception:
			self._client = None

	async def summarize(self,
					 text: str,
					 system_prompt: Optional[str] = None) -> str:
		if not self.api_key:
			raise RuntimeError("OPENAI_API_KEY не предоставлен!")
		if not self._client:
			raise RuntimeError("openai недоступен")

		prompt = text
		messages = []
		if system_prompt:
			messages.append({"role": "system", "content": system_prompt})
		messages.append({"role": "user", "content": prompt})

		def _call():
			resp = self._client.chat.completions.create(
				model=self.model or "gpt-4o-mini",
				messages=messages,
				max_tokens=800
			)
			return resp

		resp = await asyncio.to_thread(_call)
		try:
			return resp.choices[0].message.content.strip()
		except Exception as e:
			raise RuntimeError("Unexpected OpenAI response format") from e


def get_llm_client(provider: Optional[str] = None) -> LLMClient:
	prov = (provider or os.getenv("LLM_PROVIDER") or "openrouter").lower()
	if prov == "openai":
		return OpenAIClient()
	# default
	return OpenRouterClient()

