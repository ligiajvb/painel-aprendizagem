@echo off
REM Script de inicialização do Painel de Aprendizagem

echo.
echo ========================================================
echo  Painel de Aprendizagem - Inicializador
echo ========================================================
echo.

REM Verifica se Python está instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python não encontrado no PATH
    echo Instale Python de https://www.python.org/
    pause
    exit /b 1
)

echo [1/4] Verificando dependências...
if not exist "venv" (
    echo [2/4] Criando ambiente virtual...
    python -m venv venv
) else (
    echo [2/4] Ambiente virtual já existe
)

echo [3/4] Ativando ambiente virtual...
call venv\Scripts\activate.bat

echo [4/4] Instalando/atualizando dependências...
pip install -q -r requirements.txt

echo.
echo ========================================================
echo  Iniciando servidor...
echo ========================================================
echo.
echo  Acesse: http://localhost:5000
echo.

python app.py

pause
