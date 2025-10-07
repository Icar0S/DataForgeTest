@echo off
chcp 65001 > nul
echo =====================================
echo Inicialização Rápida - Modo Dev
echo =====================================

:: Definir o diretório base do projeto
set PROJECT_DIR=%~dp0

:: Ativar ambiente virtual Python
call "%PROJECT_DIR%.venv\Scripts\activate.bat"

:: Iniciar backend em uma nova janela
echo [1/3] Iniciando backend...
start cmd /k "title Backend && cd %PROJECT_DIR%src && %PROJECT_DIR%.venv\Scripts\python.exe api.py"

:: Aguardar backend verificando health check
echo [2/3] Aguardando backend iniciar...
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

:: Iniciar frontend
echo [3/3] Iniciando frontend...
start cmd /k "title Frontend && cd %PROJECT_DIR%frontend\frontend && npm start"

echo.
echo Serviços iniciados!
echo - Backend: http://localhost:5000
echo - Frontend: http://localhost:3000
echo.
echo Pressione qualquer tecla para fechar esta janela...
pause > nul