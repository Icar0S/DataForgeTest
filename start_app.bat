@echo off
echo Iniciando Data Quality Chatbot...

:: Definir o diretório base do projeto
set PROJECT_DIR=%~dp0

:: Ativar ambiente virtual Python
echo Ativando ambiente virtual Python...
call "%PROJECT_DIR%.venv\Scripts\activate.bat"

:: Instalar dependências do backend se necessário
echo Verificando dependencias do backend...
cd "%PROJECT_DIR%src\rag"
pip install -r requirements.txt > nul 2>&1

:: Instalar dependências do frontend se necessário
echo Verificando dependencias do frontend...
cd "%PROJECT_DIR%frontend\frontend"
call npm install > nul 2>&1

:: Iniciar backend em uma nova janela
echo Iniciando backend...
start cmd /k "title Backend && cd %PROJECT_DIR%src && %PROJECT_DIR%.venv\Scripts\python.exe api.py"

:: Aguardar alguns segundos para o backend inicializar
timeout /t 5 /nobreak > nul

:: Iniciar frontend em uma nova janela
echo Iniciando frontend...
start cmd /k "title Frontend && cd %PROJECT_DIR%frontend\frontend && npm start"

:: Abrir o navegador após alguns segundos
timeout /t 5 /nobreak > nul
start http://localhost:3000

echo.
echo SISTEMA INICIADO!
echo Backend: http://localhost:5000
echo Frontend: http://localhost:3000
echo.
echo Pressione qualquer tecla para fechar esta janela...
pause > nul