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

# Código HTML compacto injetando o script de forma externa para evitar quebras de texto
HTML_FINAL = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>Cobrinha Ultra Global</title>
    <link rel="stylesheet" href="https://jsdelivr.net" onerror="this.onerror=null;this.href='https://githack.com';">
</head>
<body>
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
        <div class="controles-sistema"><button class="btn-sys" id="btnPausa">Pausar</button><button class="btn-sys" id="btnReset" style="background:#e74c3c;">Resetar</button></div>
        <div class="dpad">
            <button class="btn-dir" data-dir="C">▲</button>
            <div class="dpad-row" style="margin:10px 0;"><button class="btn-dir" data-dir="E">◀</button><button class="btn-dir" data-dir="D">▶</button></div>
            <button class="btn-dir" data-dir="B">▼</button>
        </div>
    </div>
    <script src="https://github.io" onerror="var s=document.createElement('script');s.src='https://githack.com;"></script>
</body>
</html>"""

@app.route('/')
def index():
    return render_template_string(HTML_FINAL)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
