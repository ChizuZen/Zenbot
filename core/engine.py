import os
from pathlib import Path

# Configurações básicas
BASE_DIR = Path(__file__).resolve().parent.parent

def montar_prompt(pergunta, estilo="padrao"):
    """
    Versão ultraleve para o Render Free.
    Foca na personalidade do Mestre Chizu sem estourar a memória RAM.
    """
    system_prompt = (
        "Você é o Mestre Chizu, um mestre Zen inspirado em Shunryu Suzuki e Thich Nhat Hanh. "
        "Sua linguagem é poética, breve e profunda. Não use emojis."
    )
    
    # Se quiser adicionar um 'contexto' fixo sem carregar arquivos:
    contexto = "A essência do Zen é a mente de principiante. Responda com presença."

    return [
        {"role": "system", "content": f"{system_prompt}\n\nEnsinamento base: {contexto}"},
        {"role": "user", "content": pergunta}
    ]