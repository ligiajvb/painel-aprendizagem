# Vercel entry point
from app import app

# Handler para Vercel Serverless Functions
def handler(environ, start_response):
    """Handler para Vercel"""
    return app(environ, start_response)
