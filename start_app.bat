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
cd "%PROJECT_DIR%frontend\"
call npm install > nul 2>&1

:: Iniciar backend em uma nova janela
echo Iniciando backend...
start cmd /k "title Backend && cd %PROJECT_DIR%src && %PROJECT_DIR%.venv\Scripts\python.exe api.py"

:: Aguardar backend inicializar verificando health check
echo Aguardando backend inicializar...
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
        echo AVISO: Backend nao respondeu em 30s, continuando mesmo assim...
    )
) else (
    echo Backend pronto!
)

:: Iniciar frontend em uma nova janela
echo Iniciando frontend...
start cmd /k "title Frontend && cd %PROJECT_DIR%frontend\ && npm start"

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