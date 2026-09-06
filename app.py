import os, sys
from flask import Flask, render_template_string, jsonify, request

app = Flask(__name__)

# Banco de dados simulado em memória no servidor (Persiste globalmente enquanto o app estiver rodando)
# Estrutura: {"nome": pontuacao_maxima}
banco_recordes_global = {
    "Lucas": 150,
    "SnakeMaster": 100,
    "Player1": 50,
    "Cobrinha": 30,
    "iOS_User": 20
}

@app.route('/api/recordes', methods=['GET'])
def obter_recordes():
    # Ordena os recordes do maior para o menor e pega os 5 melhores
    top_5 = sorted(banco_recordes_global.items(), key=lambda item: item[1], reverse=True)[:5]
    return jsonify([{"nome": nome, "pontos": pontos} for nome, pontos in top_5])

@app.route('/api/salvar', methods=['POST'])
def salvar_recorde():
    dados = request.json
    nome = dados.get('nome', '').strip()
    pontos = int(dados.get('pontos', 0))
    
    if not nome:
        return jsonify({"status": "erro", "mensagem": "Nome inválido"}), 400
        
    # Só grava se for um nome novo ou se a pontuação atual for maior que o recorde antigo dele
    if nome not in banco_recordes_global or pontos > banco_recordes_global[nome]:
        banco_recordes_global[nome] = pontos
        
    return jsonify({"status": "sucesso"})

HTML_JOGO = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no, viewport-fit=cover">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
    <title>Cobrinha Ultra Global</title>
    <style>
        * { box-sizing: border-box; touch-action: none; -webkit-tap-highlight-color: transparent; }
        body { margin:0; background:#1e1e1e; display:flex; flex-direction:column; align-items:center; justify-content:center; min-height:100vh; color:white; font-family:Arial, sans-serif; user-select:none; padding:10px; }
        #container-principal { display: flex; flex-direction: column; align-items: center; width: 100%; max-width: 600px; }
        #placar-externo { display: flex; justify-content: space-between; width: 100%; background: #2c3e50; border: 4px solid #3498db; border-bottom: none; border-top-left-radius: 10px; border-top-right-radius: 10px; padding: 10px 20px; font-size: 16px; font-weight: bold; width: 100%; }
        #canvas-container { border: 4px solid #3498db; background:#1e1e1e; width: 100%; position: relative; }
        canvas { display:block; width: 100%; height:auto; background: #1e1e1e; }
        
        /* Painel do Ranking Global */
        #painel-ranking { width: 100%; background: #2c3e50; border: 4px solid #3498db; border-top: none; border-bottom-left-radius: 10px; border-bottom-right-radius: 10px; padding: 10px 20px; font-size: 14px; }
        #painel-ranking h3 { margin: 0 0 8px 0; text-align: center; color: #f1c40f; font-size: 16px; }
        .linha-rank { display: flex; justify-content: space-between; margin-bottom: 4px; padding-bottom: 2px; border-bottom: 1px solid #34495e; }
        
        /* Tela de Bloqueio de Login Inicial */
        #tela-login { position: absolute; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.9); display: flex; flex-direction: column; align-items: center; justify-content: center; z-index: 10; padding: 20px; text-align: center; }
        #tela-login h2 { color: #3498db; margin-bottom: 15px; }
        #input-nome { padding: 12px; font-size: 16px; border: 2px solid #3498db; border-radius: 6px; width: 80%; max-width: 280px; margin-bottom: 15px; background: #fff; color: #000; text-align: center; font-weight: bold; }
        #btn-jogar { background: #2ecc71; color: white; font-size: 18px; font-weight: bold; border: none; padding: 12px 30px; border-radius: 6px; cursor: pointer; box-shadow: 0 4px #27ae60; }
        #btn-jogar:active { transform: translateY(2px); box-shadow: 0 2px #27ae60; }

        .controles-sistema { display:none; gap:10px; margin-top:10px; width:100%; max-width:360px; }
        .btn-sys { background:#555; color:white; border:none; padding:10px; font-size:14px; font-weight:bold; border-radius:6px; flex:1; }
        .dpad { display:none; flex-direction:column; align-items:center; margin-top:15px; width:100%; max-width:260px; }
        .dpad-row { display:flex; justify-content:space-between; width:100%; gap:60px; }
        .btn-dir { background:#3498db; color:white; border:none; width:65px; height:55px; font-size:22px; font-weight:bold; border-radius:10px; box-shadow:0 4px #2980b9; display:flex; align-items:center; justify-content:center; }
        .btn-dir:active { box-shadow:0 1px #2980b9; transform:translateY(3px); background:#2980b9; }
        @media (max-width: 768px) { .controles-sistema, .dpad { display:flex; } }
    </style>
</head>
<body>
    <div id="container-principal">
        <div id="placar-externo">
            <span id="txtJogador">Jogador: --</span>
            <span id="txtPontos">Pontos: 0</span>
            <span id="txtFPS" style="color:#2ecc71;">FPS: --</span>
        </div>
        
        <div id="canvas-container">
            <!-- Tela de Login Obrigatória -->
            <div id="tela-login">
                <h2>COBRINHA GLOBAL</h2>
                <input type="text" id="input-nome" placeholder="DIGITE SEU NOME" maxlength="12">
                <button id="btn-jogar">ENTRAR E JOGAR</button>
            </div>
            <canvas id="gameCanvas" width="600" height="400"></canvas>
        </div>
        
        <!-- Novo Label: Top 5 Líderes Mundiais -->
        <div id="painel-ranking">
            <h3>🏆 TOP 5 RECORDES GLOBAIS</h3>
            <div id="lista-ranking">Carregando recordes mundiais...</div>
        </div>

        <div class="controles-sistema">
            <button class="btn-sys" id="btnPausa">Pausar</button>
            <button class="btn-sys" id="btnReset" style="background:#e74c3c;">Resetar</button>
        </div>
        <div class="dpad">
            <button class="btn-dir" data-dir="C">▲</button>
            <div class="dpad-row" style="margin:10px 0;"><button class="btn-dir" data-dir="E">◀</button><button class="btn-dir" data-dir="D">▶</button></div>
            <button class="btn-dir" data-dir="B">▼</button>
        </div>
    </div>

    <script>
        const canvas = document.getElementById("gameCanvas"), ctx = canvas.getContext("2d");
        const BLOCO = 20, LARGURA = canvas.width, ALTURA = canvas.height;
        let estado = "LOGIN", pontos = 0, vel = 10, x, y, vx = 0, vy = 0, corpo = [], tam = 1, cx, cy, direcaoAtual = "PARADO", tUltimoFrame = 0, contFrames = 0, tUltimoFPS = 0, cPendentes = [], nomeJogador = "";
        const elPontos = document.getElementById("txtPontos"), elFPS = document.getElementById("txtFPS"), elJogador = document.getElementById("txtJogador"), elListaRanking = document.getElementById("lista-ranking");
        
        document.addEventListener('gesturestart', e => e.preventDefault());
        document.addEventListener('touchstart', e => { if (estado !== "LOGIN" && e.touches.length > 1) e.preventDefault(); }, { passive: false });
        let uToque = 0; document.addEventListener('touchend', e => { const t = performance.now(); if (estado !== "LOGIN" && t - uToque <= 300) e.preventDefault(); uToque = t; }, { passive: false });

        // Função para carregar os Top 5 Recordes do Servidor
        async function carregarRankingGlobal() {
            try {
                const res = await fetch('/api/recordes');
                const dados = await res.json();
                elListaRanking.innerHTML = "";
                dados.forEach((r, i) => {
                    elListaRanking.innerHTML += `<div class="linha-rank"><span>${i+1}°. ${r.nome}</span><strong>${r.pontos} pts</strong></div>`;
                });
            } catch (err) {
                elListaRanking.innerHTML = "Erro ao carregar ranking.";
            }
        }

        // Envia a pontuação para o servidor quando morre
        async function enviarPontuacaoServidor() {
            if(!nomeJogador) return;
            try {
                await fetch('/api/salvar', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ nome: nomeJogador, pontos: pontos })
                });
                carregarRankingGlobal();
            } catch (err) {
                console.error("Erro ao salvar recorde:", err);
            }
        }

        // --- Adicione aqui o restante da mecânica do jogo (loop principal, controles, colisão etc.) se necessário ---
        // Exemplo mínimo para inicializar o fluxo do botão jogar:
        document.getElementById("btn-jogar").onclick = () => {
            const nomeIn = document.getElementById("input-nome").value.trim();
            if(nomeIn) {
                nomeJogador = nomeIn;
                elJogador.innerText = "Jogador: " + nomeJogador;
                document.getElementById("tela-login").style.display = "none";
                estado = "JOGANDO";
                carregarRankingGlobal();
            }
        };

        // Carrega o ranking ao abrir a página
        carregarRankingGlobal();
    </script>
</body>
</html>"""

@app.route('/')
def index():
    return render_template_string(HTML_JOGO)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
