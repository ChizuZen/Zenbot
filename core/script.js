const PALAVRAS_SAIDA = ['sair', 'exit', 'quit', 'gassho', 'obrigado', 'ok'];

// ID único por sessão — gerado ao abrir a aba, some ao fechar
const SESSION_ID = crypto.randomUUID();

// Mapa de @ para nome exato do autor no JSON
const AUTORES_MAP = {
    'dogen':   'Eihei Dogen',
    'osho':    'Osho',
    'haemin':  'Haemin Sunim',
    'sunim':   'Haemin Sunim',
    'masuno':  'Shunmyo Masuno',
    'suzuki':  'Shunryu Suzuki',
    'thich':   'Thich Nhat Hanh',
    'hanh':    'Thich Nhat Hanh',
};

const input       = document.getElementById('pergunta');
const respostaDiv = document.getElementById('resposta');
const btnMic      = document.getElementById('btn-mic');

function randomMsg(arr) {
    return arr[Math.floor(Math.random() * arr.length)];
}

function parsearPergunta(texto) {
    const match = texto.match(/^@(\w+)\s+(.*)/);
    if (match) {
        const chave = match[1].toLowerCase();
        const autor = AUTORES_MAP[chave] || null;
        const pergunta = match[2].trim();
        return { pergunta, autor };
    }
    return { pergunta: texto, autor: null };
}

function limparParaVoz(texto) {
    return texto
        .replace(/— via .*$/gm, '')
        .replace(/\*\*(.*?)\*\*/g, '$1')
        .replace(/\*(.*?)\*/g, '$1')
        .replace(/#{1,6}\s/g, '')
        .replace(/<[^>]+>/g, '')
        .trim();
}

// --- SÍNTESE DE VOZ ---
let falando = false;

function falar(texto) {
    if (!window.speechSynthesis) return;
    window.speechSynthesis.cancel();
    const fala = new SpeechSynthesisUtterance(limparParaVoz(texto));
    fala.lang  = 'pt-BR';
    fala.rate  = 0.9;
    fala.pitch = 1.0;
    fala.onstart = () => {
        falando = true;
        atualizarBotaoVoz();
    };
    fala.onend = () => {
        falando = false;
        atualizarBotaoVoz();
    };
    window.speechSynthesis.speak(fala);
}

function pausarVoz() {
    if (window.speechSynthesis.speaking && !window.speechSynthesis.paused) {
        window.speechSynthesis.pause();
        falando = false;
        atualizarBotaoVoz();
    } else if (window.speechSynthesis.paused) {
        window.speechSynthesis.resume();
        falando = true;
        atualizarBotaoVoz();
    }
}

function pararVoz() {
    window.speechSynthesis.cancel();
    falando = false;
    atualizarBotaoVoz();
}

function atualizarBotaoVoz() {
    const btnFalar = document.getElementById('btn-falar');
    if (btnFalar) btnFalar.textContent = falando ? 'Pausar' : 'Ouvir';
}

// --- MICROFONE ---
let reconhecendo = false;
let recognition  = null;
const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

function iniciarMicrofone() {
    if (!SpeechRecognition) {
        respostaDiv.innerHTML = '<em>Seu navegador não suporta reconhecimento de voz.</em>';
        return;
    }
    if (reconhecendo) return;

    recognition = new SpeechRecognition();
    recognition.lang            = 'pt-BR';
    recognition.interimResults  = false;
    recognition.maxAlternatives = 1;

    recognition.onstart = () => {
        reconhecendo = true;
        btnMic.classList.add('ouvindo');
        btnMic.title      = 'Solte para enviar';
        input.placeholder = 'Ouvindo...';
        respostaDiv.innerHTML = '<em>Chizu ouvindo...</em>';
    };

    recognition.onresult = (e) => {
        input.value = e.results[0][0].transcript;
    };

    recognition.onerror = () => {
        reconhecendo = false;
        btnMic.classList.remove('ouvindo');
        btnMic.title      = 'Falar com Chizu';
        input.placeholder = 'Fale com Chizu...';
        respostaDiv.innerHTML = '<em>Não consegui ouvir — tente novamente.</em>';
    };

    recognition.onend = () => {
        reconhecendo = false;
        btnMic.classList.remove('ouvindo');
        btnMic.title      = 'Falar com Chizu';
        input.placeholder = 'Fale com Chizu...';
        if (input.value.trim()) fazerPergunta();
    };

    recognition.start();
}

function pararMicrofone(e) {
    e.preventDefault();
    if (recognition && reconhecendo) {
        recognition.stop();
    }
}

// --- INICIALIZAÇÃO ---
window.addEventListener('DOMContentLoaded', () => {
    respostaDiv.innerHTML = `<em>O silêncio precede a resposta...</em>`;
    if (btnMic) {
        btnMic.addEventListener('mousedown',  iniciarMicrofone);
        btnMic.addEventListener('mouseup',    pararMicrofone);
        btnMic.addEventListener('touchstart', (e) => { e.preventDefault(); iniciarMicrofone(); }, { passive: false });
        btnMic.addEventListener('touchend',   pararMicrofone);
    }
});

// --- ENVIO DA PERGUNTA ---
async function fazerPergunta() {
    const textoRaw = input.value.trim();
    if (!textoRaw) return;

    if (PALAVRAS_SAIDA.includes(textoRaw.toLowerCase())) {
        const despedida = randomMsg(window.DESPEDIDA_JS);
        respostaDiv.innerHTML = `<em>${despedida}</em>`;
        falar(despedida);
        input.value    = '';
        input.disabled = true;
        return;
    }

    const { pergunta, autor } = parsearPergunta(textoRaw);

    const mestreSelect    = document.getElementById('mestre-select');
    const mestreEscolhido = mestreSelect ? mestreSelect.value : "";

    input.disabled    = true;
    input.placeholder = mestreEscolhido ? `Consultando ${mestreEscolhido}...` : autor ? `Consultando ${autor}...` : 'Chizu medita...';
    respostaDiv.innerHTML = `<em>${randomMsg(window.AGUARDANDO_JS)}<br><br>     Chizu refletindo...</em>`;

    try {
        const payload = { pergunta, session_id: SESSION_ID };
        if (mestreEscolhido) {
            payload.autor = mestreEscolhido;
        } else if (autor) {
            payload.autor = autor;
        }

        const response = await fetch('/ask', {
            method:  'POST',
            headers: { 'Content-Type': 'application/json' },
            body:    JSON.stringify(payload)
        });

        const data     = await response.json();
        const resposta = data.resposta;

        const respostaHTML = resposta
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\*(.*?)\*/g, '<em>$1</em>')
            .replace(/^\* (.+)/gm, '<li>$1</li>')
            .replace(/(<li>.*<\/li>)/gs, '<ul>$1</ul>')
            .replace(/\n\n/g, '</p><p>')
            .replace(/\n/g, '<br>')
            .replace(/\. ([A-ZÁÉÍÓÚÂÊÎÔÛÃÕÀÇ])/g, '.</p><p>$1');

        respostaDiv.innerHTML = `
            <p>${respostaHTML}</p>
            <div class="share-buttons">
                <button id="btn-falar"   title="Ouvir">Ouvir</button>
                <button id="btn-parar"   title="Parar">Parar</button>
                <button id="btn-whatsapp">WhatsApp</button>
                <button id="btn-email">Email</button>
            </div>
        `;

        document.getElementById('btn-falar').addEventListener('click', () => {
            if (falando) { pausarVoz(); }
            else if (window.speechSynthesis.paused) { pausarVoz(); }
            else { falar(resposta); }
        });
        document.getElementById('btn-parar').addEventListener('click',    () => pararVoz());
        document.getElementById('btn-whatsapp').addEventListener('click', () => compartilharWhatsApp(resposta));
        document.getElementById('btn-email').addEventListener('click',    () => compartilharEmail(resposta));

    } catch (error) {
        respostaDiv.innerHTML = '<em>(o vento levou sua pergunta...)</em>';
    } finally {
        input.disabled    = false;
        input.value       = '';
        input.placeholder = 'Fale com Chizu...';
        input.focus();
    }
}

input.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') fazerPergunta();
});

function compartilharWhatsApp(texto) {
    const msg = encodeURIComponent("Mestre Chizu:\n\n" + texto + "\n\nhttp://chizu.ia.br");
    window.open(`https://wa.me/?text=${msg}`, '_blank');
}

function compartilharEmail(texto) {
    const assunto = encodeURIComponent("Um ensinamento do Mestre Chizu");
    const corpo   = encodeURIComponent("Mestre Chizu:\n\n" + texto + "\n\nhttp://chizu.ia.br");
    window.open(`mailto:?subject=${assunto}&body=${corpo}`, '_blank');
}
