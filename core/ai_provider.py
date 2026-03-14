import os
import requests
import random
import time  # Importante para a pausa

class FreeAIProvider:
    def __init__(self):
        self.keys = {
            "gemini": os.getenv("GEMINI_API_KEY"),
            "groq": os.getenv("GROQ_API_KEY"),
            "sambanova": os.getenv("SAMBANOVA_API_KEY"),
            "cerebras": os.getenv("CEREBRAS_API_KEY")

        }

    def chat(self, messages, temperature=0.45, max_tokens=500, top_p=0.9, frequency_penalty=0.45, presence_penalty=0.25):
        providers = [
            ("Gemini", self._gemini_chat),
            ("Groq", self._groq_chat),
            ("SambaNova", self._sambanova_chat),
            ("Cerebras", self._cerebras_chat),
        ]

        random.shuffle(providers)

        for name, method in providers:
            if not self.keys.get(name.lower()):
                continue
            try:
                # O mestre tenta falar...
                resposta = method(messages, temperature, max_tokens, top_p, frequency_penalty, presence_penalty)
                return resposta, name
            
            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 429:
                    print(f"[AI] {name} está exausto (429). Meditando por 2 segundos...")
                    time.sleep(2) # O respiro zen
                else:
                    print(f"[AI] {name} falhou com erro HTTP: {e}")
                continue
            except Exception as e:
                print(f"[AI] {name} falhou: {e}. Tentando próximo...")
                continue

        # Se todos falharem, o sistema retorna o silêncio que será tratado pelo seu zen.py
        return "Caminhante, o silêncio envolve essa questão;", "Fallback"



    def _gemini_chat(self, messages, temperature, max_tokens, top_p, freq_pen, pres_pen):
        model_name = "gemini-2.5-flash" 
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={self.keys['gemini']}"
        contents = []
        for m in messages:
            role = "model" if m["role"] == "assistant" else "user"
            contents.append({"role": role, "parts": [{"text": m["content"]}]})
        payload = {
            "contents": contents,
            "generationConfig": {"temperature": temperature, "maxOutputTokens": max_tokens, "topP": top_p}
        }
        r = requests.post(url, json=payload, timeout=20)
        r.raise_for_status()
        return r.json()["candidates"][0]["content"]["parts"][0]["text"]

    def _groq_chat(self, messages, temperature=0.4, max_tokens=1000, top_p=0.9, frequency_penalty=0.10, presence_penalty=0.20):
        payload = {
            "model": "llama-3.3-70b-versatile",
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        r = requests.post("https://api.groq.com/openai/v1/chat/completions",
                         headers={"Authorization": f"Bearer {self.keys['groq']}"},
                         json=payload, timeout=20)
        r.raise_for_status()
        return r.json()["choices"][0]["message"]["content"]

    def _cerebras_chat(self, messages, temperature, max_tokens, top_p, freq_pen, pres_pen):
        payload = {
            "model": "llama3.1-8b",
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        r = requests.post("https://api.cerebras.ai/v1/chat/completions",
                         headers={"Authorization": f"Bearer {self.keys['cerebras']}"},
                         json=payload, timeout=20)
        r.raise_for_status()
        return r.json()["choices"][0]["message"]["content"]

    def _sambanova_chat(self, messages, temperature, max_tokens, top_p, freq_pen, pres_pen):
        payload = {
            "model": "Meta-Llama-3.1-8B-Instruct",
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        r = requests.post("https://api.sambanova.ai/v1/chat/completions",
                         headers={"Authorization": f"Bearer {self.keys['sambanova']}"},
                         json=payload, timeout=30)
        r.raise_for_status()
        return r.json()["choices"][0]["message"]["content"]