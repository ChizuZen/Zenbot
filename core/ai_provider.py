import os
import requests
import random

class FreeAIProvider:
    def __init__(self):
        self.keys = {
            "gemini": os.getenv("GEMINI_API_KEY"),             
            "groq": os.getenv("GROQ_API_KEY"),
            "sambanova": os.getenv("SAMBANOVA_API_KEY"),
            "cerebras": os.getenv("CEREBRAS_API_KEY")
        }

    def chat(self, messages, temperature=0.4, max_tokens=180, 
             top_p=0.9, frequency_penalty=0.0, presence_penalty=0.0):
        
        providers = [
            (self._gemini_chat, "Gemini"),
            (self._groq_chat, "Groq"),
            (self._sambanova_chat, "SambaNova"),
            (self._cerebras_chat, "Cerebras")
        ]

        random.shuffle(providers) 

        for method, name in providers:
            if not self.keys.get(name.lower()):
                continue
            try:
                # Agora passamos todos os parâmetros para os métodos
                res = method(messages, temperature, max_tokens, top_p, frequency_penalty, presence_penalty)
                # RETORNA UMA TUPLA: (Texto, Nome da IA)
                return res, name 
            except Exception as e:
                print(f"[AI] {name} falhou: {e}. Tentando próxima...")
                continue
        
        return "O mestre entrou em silêncio profundo.", "Erro/Nenhum"

    def _groq_chat(self, messages, temperature, max_tokens, top_p, freq_pen, pres_pen):
        payload = {
            "model": "llama-3.3-70b-versatile",
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "top_p": top_p,
            "frequency_penalty": freq_pen,
            "presence_penalty": pres_pen
        }
        r = requests.post("https://api.groq.com/openai/v1/chat/completions",
                          headers={"Authorization": f"Bearer {self.keys['groq']}"},
                          json=payload, timeout=15)
        r.raise_for_status()
        return r.json()["choices"][0]["message"]["content"]

    def _cerebras_chat(self, messages, temperature, max_tokens, top_p, freq_pen, pres_pen):
        payload = {
            "model": "llama3.1-8b", 
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "top_p": top_p
        }
        r = requests.post("https://api.cerebras.ai/v1/chat/completions", 
                          headers={"Authorization": f"Bearer {self.keys['cerebras']}"}, 
                          json=payload, timeout=15)
        r.raise_for_status()
        return r.json()["choices"][0]["message"]["content"]

    def _sambanova_chat(self, messages, temperature, max_tokens, top_p, freq_pen, pres_pen):
        payload = {
            "model": "Meta-Llama-3.1-8B-Instruct", 
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "top_p": top_p
        }
        r = requests.post("https://api.sambanova.ai/v1/chat/completions", 
                          headers={"Authorization": f"Bearer {self.keys['sambanova']}"}, 
                          json=payload, timeout=25)
        r.raise_for_status()
        return r.json()["choices"][0]["message"]["content"]

    def _gemini_chat(self, messages, temperature, max_tokens, top_p, freq_pen, pres_pen):
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-lite-preview:generateContent?key={self.keys['gemini']}"
        contents = []
        for m in messages:
            role = "model" if m["role"] == "assistant" else "user"
            contents.append({"role": role, "parts": [{"text": m["content"]}]})
        payload = {
            "contents": contents,
            "generationConfig": {"temperature": temperature, "maxOutputTokens": max_tokens, "topP": top_p}
        }
        r = requests.post(url, json=payload, timeout=15)
        r.raise_for_status()
        return r.json()["candidates"][0]["content"]["parts"][0]["text"]