import os
from flask import Flask, render_template, jsonify, request

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
    # Coleta os itens do dicionário (chave, valor) -> (nome, pontos)
    ranking = [{"nome": k, "pontos": v} for k, v in banco_recordes_global.items()]
    # Corrige a ordenação usando a chave correta 'pontos'
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

@app.route('/')
def index():
    # Renderiza o arquivo HTML localizado na pasta templates/
    return render_template('jogo.html')

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
