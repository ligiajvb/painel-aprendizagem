#!/bin/bash

# Script de inicialização do Painel de Aprendizagem (Linux/Mac)

echo ""
echo "========================================================"
echo " Painel de Aprendizagem - Inicializador"
echo "========================================================"
echo ""

# Verifica se Python está instalado
if ! command -v python3 &> /dev/null; then
    echo "Erro: Python não encontrado"
    echo "Instale Python de https://www.python.org/"
    exit 1
fi

echo "[1/4] Verificando dependências..."
if [ ! -d "venv" ]; then
    echo "[2/4] Criando ambiente virtual..."
    python3 -m venv venv
else
    echo "[2/4] Ambiente virtual já existe"
fi

echo "[3/4] Ativando ambiente virtual..."
source venv/bin/activate

echo "[4/4] Instalando/atualizando dependências..."
pip install -q -r requirements.txt

echo ""
echo "========================================================"
echo " Iniciando servidor..."
echo "========================================================"
echo ""
echo " Acesse: http://localhost:5000"
echo ""

python3 app.py
