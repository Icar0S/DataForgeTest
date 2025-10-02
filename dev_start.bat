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

:: Aguardar backend (máximo 10 segundos)
echo [2/3] Aguardando backend iniciar...
set /a counter=0
:wait_backend
timeout /t 1 /nobreak > nul
netstat -an | find ":5000" > nul
if %errorlevel% neq 0 (
    set /a counter+=1
    if %counter% lss 10 goto wait_backend
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