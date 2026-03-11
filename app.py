from flask import Flask, render_template, jsonify, request
from sheets_manager import sheets_manager
from datetime import datetime
import os
import traceback

app = Flask(__name__, template_folder='template', static_folder='static')

# Configuração para Vercel
app.config['JSON_AS_ASCII'] = False

# Error handlers
@app.errorhandler(Exception)
def handle_exception(e):
    """Handle all exceptions"""
    print(f"Error: {str(e)}")
    print(traceback.format_exc())
    return jsonify({
        "error": "Internal server error",
        "message": str(e),
        "demo_mode": True
    }), 500

@app.errorhandler(404)
def handle_404(e):
    """Handle 404 errors"""
    return jsonify({"error": "Not found"}), 404

# ==================== ROTAS ====================

@app.route('/')
def index():
    """Página principal"""
    return render_template('index.html')


@app.route('/api/data')
def api_data():
    """Endpoint para obter todos os dados"""
    try:
        return jsonify(sheets_manager.get_all_data())
    except Exception as e:
        return jsonify({"error": str(e), "data": {}})


@app.route('/api/sheet/<sheet_name>')
def api_sheet(sheet_name):
    """Endpoint para obter dados de uma aba específica"""
    try:
        data = sheets_manager.get_sheet_data(sheet_name)
        if data:
            return jsonify(data)
        return jsonify({"error": "Aba não encontrada"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/sync', methods=['POST'])
def api_sync():
    """Endpoint para sincronizar manualmente"""
    try:
        success = sheets_manager.sync_data()
        return jsonify({
            "success": success,
            "status": sheets_manager.get_status()
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "status": sheets_manager.get_status()
        })


@app.route('/api/status')
def api_status():
    """Endpoint para status da conexão"""
    try:
        status = sheets_manager.get_status()
        status['timestamp'] = datetime.now().isoformat()
        return jsonify(status)
    except Exception as e:
        return jsonify({
            "connected": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        })


@app.route('/api/raw')
def api_raw():
    """Endpoint para dados brutos"""
    try:
        all_data = sheets_manager.get_all_data()
        return jsonify(all_data)
    except Exception as e:
        return jsonify({"error": str(e), "data": {}})


# ==================== CONFIGURAÇÃO ====================

if __name__ == '__main__':
    print("\n" + "="*50)
    print("🚀 Iniciando Painel de Aprendizagem")
    print("="*50)
    print("\n📊 Modo demonstração ativo")
    print("\n✓ Servidor iniciado!")
    print("📍 Acesso em: http://localhost:5000")
    print("="*50 + "\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
