# Vercel entry point
import os
os.environ['VERCEL'] = '1'

from app import app

# Detecta ambiente Vercel
if os.getenv('VERCEL'):
    print("🌐 Detectado ambiente Vercel - usando modo demo")

# Vercel serverless function handler
def handler(environ, start_response):
    """Handler para Vercel Serverless Functions"""
    
    # Adiciona headers CORS
    def custom_start_response(status, headers, exc_info=None):
        headers.append(('Access-Control-Allow-Origin', '*'))
        headers.append(('Access-Control-Allow-Methods', 'GET, POST, OPTIONS'))
        headers.append(('Access-Control-Allow-Headers', 'Content-Type'))
        return start_response(status, headers, exc_info)
    
    return app.wsgi_app(environ, custom_start_response)
