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

    def chat(self, messages, temperature=0.4, max_tokens=180):
        # Lista de provedores disponíveis
        providers = [
            (self._gemini_chat, "Gemini"),
            (self._groq_chat, "Groq"),
            (self._sambanova_chat, "SambaNova"),
            (self._cerebras_chat, "Cerebras")
        ]

        # O mestre embaralha as opções para o equilíbrio perfeito
        random.shuffle(providers) 

        for method, name in providers:
            if not self.keys.get(name.lower()):
                continue
            try:
                print(f"[AI] Escolhida: {name}. Processando...")
                return method(messages, temperature, max_tokens)
            except Exception as e:
                print(f"[AI] {name} falhou: {e}. Tentando próxima...")
                continue
        
        raise RuntimeError("Todas as fontes de sabedoria falharam.")

    def _groq_chat(self, messages, temperature, max_tokens):
        payload = {
            "model": "llama-3.3-70b-versatile",
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        r = requests.post("https://api.groq.com/openai/v1/chat/completions",
                          headers={"Authorization": f"Bearer {self.keys['groq']}"},
                          json=payload, timeout=15)
        r.raise_for_status()
        return r.json()["choices"][0]["message"]["content"]



    def _sambanova_chat(self, messages, temperature, max_tokens):
        headers = {"Authorization": f"Bearer {self.keys['sambanova']}", "Content-Type": "application/json"}
        payload = {
            "model": "Llama-3.1-405B-Instruct",
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        r = requests.post("https://api.sambanova.ai/v1/chat/completions", headers=headers, json=payload, timeout=25)
        r.raise_for_status()
        return r.json()["choices"][0]["message"]["content"]

    def _gemini_chat(self, messages, temperature, max_tokens):
        # Ajuste na URL para garantir a versão estável
        url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={self.keys['gemini']}"
        
        prompt = ""
        for m in messages:
            role = "model" if m["role"] == "assistant" else "user"
            prompt += f"{role}: {m['content']}\n"
        
        payload = {
            "contents": [{"parts":[{"text": prompt}]}],
            "generationConfig": {
                "temperature": temperature,
                "maxOutputTokens": max_tokens
            }
        }
        r = requests.post(url, json=payload, timeout=15)
        r.raise_for_status()
        return r.json()["candidates"][0]["content"]["parts"][0]["text"]

    def _cerebras_chat(self, messages, temperature, max_tokens):
        headers = {
            "Authorization": f"Bearer {self.keys['cerebras']}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "llama3.1-8b", # Confirme se é este o modelo no seu dashboard
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        # Tente usar a URL sem o /v1 se o erro persistir, mas o padrão é:
        r = requests.post("https://api.cerebras.ai/v1/chat/completions", 
                          headers=headers, json=payload, timeout=15)
        r.raise_for_status()
        return r.json()["choices"][0]["message"]["content"]