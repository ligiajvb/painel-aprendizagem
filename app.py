from flask import Flask, render_template, jsonify, request
from sheets_manager import sheets_manager
import json
from datetime import datetime

app = Flask(__name__, template_folder='template', static_folder='static')

# ==================== ROTAS ====================

@app.route('/')
def index():
    """Página principal"""
    return render_template('index.html')


@app.route('/api/data')
def api_data():
    """Endpoint para obter todos os dados"""
    return jsonify(sheets_manager.get_all_data())


@app.route('/api/sheet/<sheet_name>')
def api_sheet(sheet_name):
    """Endpoint para obter dados de uma aba específica"""
    data = sheets_manager.get_sheet_data(sheet_name)
    if data:
        return jsonify(data)
    return jsonify({"error": "Aba não encontrada"}), 404


@app.route('/api/sync', methods=['POST'])
def api_sync():
    """Endpoint para sincronizar manualmente"""
    success = sheets_manager.sync_data()
    return jsonify({
        "success": success,
        "status": sheets_manager.get_status()
    })


@app.route('/api/status')
def api_status():
    """Endpoint para status da conexão"""
    status = sheets_manager.get_status()
    status['timestamp'] = datetime.now().isoformat()
    return jsonify(status)


@app.route('/api/raw')
def api_raw():
    """Endpoint para dados brutos (compatível com HTML remanescente)"""
    # Converte do formato de Sheets para o formato esperado pelo HTML
    all_data = sheets_manager.get_all_data()
    
    # Se houver estrutura esperada, retorna como está
    return jsonify(all_data)


# ==================== CONFIGURAÇÃO ====================

if __name__ == '__main__':
    # Inicia sincronização automática a cada 30 segundos
    print("\n" + "="*50)
    print("🚀 Iniciando Painel de Aprendizagem")
    print("="*50)
    
    # Sincroniza dados inicialmente
    print("\n📊 Sincronizando dados iniciais...")
    sheets_manager.sync_data()
    
    # Inicia sincronização automática
    sheets_manager.start_auto_sync(interval_seconds=30)
    
    print("\n✓ Servidor iniciado!")
    print("📍 Acesso em: http://localhost:5000")
    print("="*50 + "\n")
    
    # Inicia servidor Flask
    app.run(debug=True, host='0.0.0.0', port=5000)
