import os
import requests
import random

class FreeAIProvider:
    def __init__(self):
        # Chaves de API vindas do ambiente
        self.keys = {
            "gemini": os.getenv("GEMINI_API_KEY"),             
            "groq": os.getenv("GROQ_API_KEY"),
            "sambanova": os.getenv("SAMBANOVA_API_KEY"),
            "cerebras": os.getenv("CEREBRAS_API_KEY")
        }

    def chat(self, messages, temperature=0.4, max_tokens=180, 
             top_p=0.9, frequency_penalty=0.0, presence_penalty=0.0):
        """
        O Grande Maestro: Tenta cada provedor em sequência, 
        repassando todos os parâmetros de tuning.
        """
        # Ordem de tentativa: Groq -> Cerebras -> Sambanova -> Gemini
        
        # 1. TENTATIVA: GROQ (O mais rápido)
        try:
            return self._groq_chat(messages, temperature, max_tokens, top_p, frequency_penalty, presence_penalty)
        except Exception as e:
            print(f"[LOG] Groq falhou, tentando Cerebras... Erro: {e}")
            
        # 2. TENTATIVA: CEREBRAS
        try:
            return self._cerebras_chat(messages, temperature, max_tokens, top_p)
        except Exception as e:
            print(f"[LOG] Cerebras falhou, tentando Sambanova... Erro: {e}")

        # 3. TENTATIVA: SAMBANOVA
        try:
            return self._sambanova_chat(messages, temperature, max_tokens, top_p)
        except Exception as e:
            print(f"[LOG] Sambanova falhou, tentando Gemini... Erro: {e}")

        # 4. TENTATIVA FINAL: GEMINI (O porto seguro)
        try:
            return self._gemini_chat(messages, temperature, max_tokens, top_p)
        except Exception as e:
            print(f"[LOG] Todos os provedores falharam. Erro final: {e}")
            return "O mestre entrou em meditação profunda e não pode responder agora. Tente mais tarde."

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

    def _cerebras_chat(self, messages, temperature, max_tokens, top_p):
        headers = {
            "Authorization": f"Bearer {self.keys['cerebras']}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "llama3.1-8b", 
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "top_p": top_p
        }
        r = requests.post("https://api.cerebras.ai/v1/chat/completions", 
                          headers=headers, json=payload, timeout=15)
        r.raise_for_status()
        return r.json()["choices"][0]["message"]["content"]

    def _sambanova_chat(self, messages, temperature, max_tokens, top_p):
        headers = {
            "Authorization": f"Bearer {self.keys['sambanova']}", 
            "Content-Type": "application/json"
        }
        payload = {
            "model": "Meta-Llama-3.1-8B-Instruct", 
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "top_p": top_p
        }
        r = requests.post("https://api.sambanova.ai/v1/chat/completions", 
                          headers=headers, json=payload, timeout=25)
        r.raise_for_status()
        return r.json()["choices"][0]["message"]["content"]

    def _gemini_chat(self, messages, temperature, max_tokens, top_p):
        url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={self.keys['gemini']}"
        
        contents = []
        for m in messages:
            role = "model" if m["role"] == "assistant" else "user"
            contents.append({"role": role, "parts": [{"text": m["content"]}]})
        
        payload = {
            "contents": contents,
            "generationConfig": {
                "temperature": temperature,
                "maxOutputTokens": max_tokens,
                "topP": top_p
            }
        }
        r = requests.post(url, json=payload, timeout=15)
        r.raise_for_status()
        return r.json()["candidates"][0]["content"]["parts"][0]["text"]