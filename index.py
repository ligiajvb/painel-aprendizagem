from app import app

# Handler para Vercel Serverless
def handler(environ, start_response):
    return app(environ, start_response)
