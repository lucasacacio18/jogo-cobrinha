import os
from flask import Flask, render_template_string, jsonify, request

app = Flask(__name__)

# Banco de dados simulado em memória
banco_recordes_global = {
    "Lucas": 150,
    "SnakeMaster": 100,
    "Player1": 50,
    "Cobrinha": 30,
    "iOS_User": 20
}

@app.route('/api/recordes', methods=['GET'])
def obter_recordes():
    ranking = [{"nome": k, "pontos": v} for k, v in banco_recordes_global.items()]
    top_5 = sorted(ranking, key=lambda x: x["pontos"], reverse=True)[:5]
    return jsonify(top_5)

@app.route('/api/salvar', methods=['POST'])
def salvar_recorde():
    dados = request.json or {}
    nome = dados.get('nome', '').strip()
    pontos = int(dados.get('pontos', 0))
    
    if not nome:
        return jsonify({"status": "erro", "mensagem": "Nome inválido"}), 400
        
    if nome not in banco_recordes_global or pontos > banco_recordes_global[nome]:
        banco_recordes_global[nome] = pontos
        
    return jsonify({"status": "sucesso"})

# --- BLOCOS DE HTML SEPARADOS PARA EVITAR CORTE DE TEXTO NO COPIAR E COLAR ---
H_ESTILO = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no, viewport-fit=cover">
    <title>Cobrinha Ultra Global</title>
    <style>
        * { box-sizing: border-box; touch-action: none; -webkit-tap-highlight-color: transparent; }
        body { margin:0; background:#1e1e1e; display:flex; flex-direction:column; align-items:center; justify-content:center; min-height:100vh; color:white; font-family:Arial, sans-serif; user-select:none; padding:10px; }
        #container-principal { display: flex; flex-direction: column; align-items: center; width: 100%; max-width: 600px; }
        #placar-externo { display: flex; justify-content: space-between; width: 100%; background: #2c3e50; border: 4px solid #3498db; border-bottom: none; border-top-left-radius: 10px; border-top-right-radius: 10px; padding: 10px 20px; font-size: 16px; font-weight: bold; width: 100%; }
        #canvas-container { border: 4px solid #3498db; background:#1e1e1e; width: 100%; position: relative; }
        canvas { display:block; width: 100%; height:auto; background: #1e1e1e; }
        #painel-ranking { width: 100%; background: #2c3e50; border: 4px solid #3498db; border-top: none; border-bottom-left-radius: 10px; border-bottom-right-radius: 10px; padding: 10px 20px; font-size: 14px; }
        #painel-ranking h3 { margin: 0 0 8px 0; text-align: center; color: #f1c40f; font-size: 16px; }
        .linha-rank { display: flex; justify-content: space-between; margin-bottom: 4px; padding-bottom: 2px; border-bottom: 1px solid #34495e; }
        #tela-login { position: absolute; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.9); display: flex; flex-direction: column; align-items: center; justify-content: center; z-index: 10; padding: 20px; text-align: center; }
        #tela-login h2 { color: #3498db; margin-bottom: 15px; }
        #input-nome { padding: 12px; font-size: 16px; border: 2px solid #3498db; border-radius: 6px; width: 80%; max-width: 280px; margin-bottom: 15px; background: #fff; color: #000; text-align: center; font-weight: bold; }
        #btn-jogar { background: #2ecc71; color: white; font-size: 18px; font-weight: bold; border: none; padding: 12px 30px; border-radius: 6px; cursor: pointer; box-shadow: 0 4px #27ae60; }
        .controles-sistema { display:none; gap:10px; margin-top:10px; width:100%; max-width:360px; }
        .btn-sys { background:#555; color:white; border:none; padding:10px; font-size:14px; font-weight:bold; border-radius:6px; flex:1; }
        .dpad { display:none; flex-direction:column; align-items:center; margin-top:15px; width:100%; max-width:260px; }
        .dpad-row { display:flex; justify-content:space-between; width:100%; gap:60px; }
        .btn-dir { background:#3498db; color:white; border:none; width:65px; height:55px; font-size:22px; font-weight:bold; border-radius:10px; box-shadow:0 4px #2980b9; display:flex; align-items:center; justify-content:center; }
        @media (max-width: 768px) { .controles-sistema, .dpad { display:flex; } }
    </style>
</head>
"""

H_CORPO = """<body>
    <div id="container-principal">
        <div id="placar-externo">
            <span id="txtJogador">Jogador: --</span>
            <span id="txtPontos">Pontos: 0</span>
            <span id="txtFPS" style="color:#2ecc71;">FPS: --</span>
        </div>
        <div id="canvas-container">
            <div id="tela-login">
                <h2>COBRINHA GLOBAL</h2>
                <input type="text" id="input-nome" placeholder="DIGITE SEU NOME" maxlength="12">
                <button id="btn-jogar">ENTRAR E JOGAR</button>
            </div>
            <canvas id="gameCanvas" width="600" height="400"></canvas>
        </div>
        <div id="painel-ranking">
            <h3>🏆 TOP 5 RECORDES GLOBAIS</h3>
            <div id="lista-ranking">Carregando recordes...</div>
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
"""

H_SCRIPT = """    <script>
        const canvas = document.getElementById("gameCanvas"), ctx = canvas.getContext("2d");
        const BLOCO = 20, LARGURA = canvas.width, ALTURA = canvas.height;
        
        let estado = "LOGIN", pontos = 0, vel = 10;
        let x = 100, y = 100, vx = BLOCO, vy = 0;
        let corpo = [{x: 100, y: 100}], tam = 3;
        let cx = 200, cy = 200;
        let direcaoAtual = "DIREITA", nomeJogador = "";
        let emPausa = false, tUltimoFrame = 0, contFrames = 0, tUltimoFPS = 0;

        const elPontos = document.getElementById("txtPontos"), elFPS = document.getElementById("txtFPS");
        const elJogador = document.getElementById("txtJogador"), elListaRanking = document.getElementById("lista-ranking");
        
        document.addEventListener('gesturestart', e => e.preventDefault());

        async function carregarRankingGlobal() {
            try {
                const res = await fetch('/api/recordes');
                const dados = await res.json();
                elListaRanking.innerHTML = "";
                dados.forEach((r, i) => {
                    elListaRanking.innerHTML += `<div class="linha-rank"><span>${i+1}°. ${r.nome}</span><strong>${r.pontos} pts</strong></div>`;
                });
            } catch (err) {
                elListaRanking.innerHTML = `
                    <div class="linha-rank"><span>1°. Lucas</span><strong>150 pts</strong></div>
                    <div class="linha-rank"><span>2°. SnakeMaster</span><strong>100 pts</strong></div>
                    <div class="linha-rank"><span>3°. Player1</span><strong>50 pts</strong></div>
                `;
            }
        }

        async function enviarPontuacaoServidor() {
            if(!nomeJogador || pontos === 0) return;
            try {
                await fetch('/api/salvar', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ nome: nomeJogador, pontos: pontos })
                });
                carregarRankingGlobal();
            } catch (err) { console.error(err); }
        }

        function novaMaca() {
            cx = Math.floor(Math.random() * (LARGURA / BLOCO)) * BLOCO;
            cy = Math.floor(Math.random() * (ALTURA / BLOCO)) * BLOCO;
        }

        function resetarJogo() {
            pontos = 0; elPontos.innerText = "Pontos: " + pontos;
            x = 100; y = 100; vx = BLOCO; vy = 0; direcaoAtual = "DIREITA";
            corpo = [{x: 100, y: 100}]; tam = 3; emPausa = false;
            document.getElementById("btnPausa").innerText = "Pausar";
            novaMaca();
        }

        function loopJogo(tempoAtual) {
            requestAnimationFrame(loopJogo);
            contFrames++;
            if (tempoAtual - tUltimoFPS >= 1000) {
                elFPS.innerText = "FPS: " + contFrames;
                contFrames = 0; tUltimoFPS = tempoAtual;
            }

            if (tempoAtual - tUltimoFrame < (1000 / vel)) return;
            tUltimoFrame = tempoAtual;

            if (estado !== "JOGANDO" || emPausa) {
                if(estado === "LOGIN") { ctx.fillStyle = "#1e1e1e"; ctx.fillRect(0, 0, LARGURA, ALTURA); }
                return;
            }

            x += vx; y += vy;
            if (x < 0 || x >= LARGURA || y < 0 || y >= ALTURA) { morreu(); return; }

            for (let i = 0; i < corpo.length - 1; i++) {
                if (corpo[i].x === x && corpo[i].y === y) { morreu(); return; }
            }
            corpo.push({ x: x, y: y });
            while (corpo.length > tam) { corpo.shift(); }

            if (x === cx && y === cy) { pontos += 10; tam++; elPontos.innerText = "Pontos: " + pontos; novaMaca(); }

            ctx.fillStyle = "#1e1e1e"; ctx.fillRect(0, 0, LARGURA, ALTURA);
            ctx.fillStyle = "#e74c3c"; ctx.fillRect(cx, cy, BLOCO - 2, BLOCO - 2);
            corpo.forEach((parte, idx) => {
                ctx.fillStyle = idx === corpo.length - 1 ? "#2ecc71" : "#27ae60";
                ctx.fillRect(parte.x, parte.y, BLOCO - 2, BLOCO - 2);
            });
        }

        function morreu() { alert("Game Over! Pontos: " + pontos); enviarPontuacaoServidor(); resetarJogo(); }

        function mudarDirecao(novaDir) {
