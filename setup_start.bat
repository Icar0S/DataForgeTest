@echo off
chcp 65001 > nul
echo ================================================
echo Configuração Inicial - Data Quality Chatbot
echo ================================================

:: Definir o diretório base do projeto
set PROJECT_DIR=%~dp0

echo [1/6] Ativando ambiente virtual Python...
call "%PROJECT_DIR%.venv\Scripts\activate.bat"

:: Verificar e instalar dependências do backend
echo [2/6] Verificando dependências do backend...
cd "%PROJECT_DIR%src\rag"
python -c "import llama_index" 2>nul
if %errorlevel% neq 0 (
    echo Instalando dependências do backend...
    pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo Erro ao instalar dependências do backend.
        pause
        exit /b 1
    )
) else (
    echo Dependências do backend já instaladas.
)

:: Verificar e instalar dependências do frontend
echo [3/6] Verificando dependências do frontend...
cd "%PROJECT_DIR%frontend\frontend"
if not exist "node_modules" (
    echo Instalando dependências do frontend...
    call npm install
    if %errorlevel% neq 0 (
        echo Erro ao instalar dependências do frontend.
        pause
        exit /b 1
    )
) else (
    echo Dependências do frontend já instaladas.
)

:: Iniciar backend
echo [4/6] Iniciando backend...
start cmd /k "title Backend && cd %PROJECT_DIR%src && %PROJECT_DIR%.venv\Scripts\python.exe api.py"

:: Aguardar backend inicializar verificando health check
echo [5/6] Aguardando backend inicializar...
set /a counter=0
:wait_backend
timeout /t 1 /nobreak > nul
powershell -Command "try { $response = Invoke-WebRequest -Uri 'http://localhost:5000/' -UseBasicParsing -TimeoutSec 2 -ErrorAction Stop; exit 0 } catch { exit 1 }" > nul 2>&1
if %errorlevel% neq 0 (
    set /a counter+=1
    if %counter% lss 30 (
        echo Aguardando backend... %counter%/30s
        goto wait_backend
    ) else (
        echo Timeout ao aguardar backend.
        pause
        exit /b 1
    )
) else (
    echo Backend pronto!
)

:: Iniciar frontend
echo [6/6] Iniciando frontend...
start cmd /k "title Frontend && cd %PROJECT_DIR%frontend\frontend && npm start"

:: Aguardar frontend inicializar
echo Aguardando frontend inicializar...
set /a counter=0
:wait_frontend
timeout /t 1 /nobreak > nul
netstat -an | find ":3000" > nul
if %errorlevel% neq 0 (
    set /a counter+=1
    if %counter% lss 30 (
        echo Aguardando frontend... %counter%/30s
        goto wait_frontend
    ) else (
        echo Timeout ao aguardar frontend.
        pause
        exit /b 1
    )
)

:: Abrir navegador quando tudo estiver pronto
start http://localhost:3000

echo.
echo ================================================
echo Instalação e inicialização concluídas com sucesso!
echo ------------------------------------------------
echo Para próximas execuções, use o dev_start.bat
echo ================================================
echo.
echo Serviços ativos:
echo - Backend: http://localhost:5000
echo - Frontend: http://localhost:3000
echo.
echo Pressione qualquer tecla para fechar esta janela...
pause > nul