@echo off
REM RAG Integration Test Runner para Windows
REM Este script executa os testes de integração para o sistema RAG

echo === Executando Testes de Integracao RAG ===
echo.

REM Navegar para o diretório do frontend
cd frontend\frontend

echo 🔧 Instalando dependencias...
call npm install

echo.
echo 🧪 Executando testes unitarios do ChatWindow...
call npm test -- --testPathPattern=ChatWindow.test.js --watchAll=false --verbose

echo.
echo 🧪 Executando testes de integracao do SupportPage...
call npm test -- --testPathPattern=SupportPage.test.js --watchAll=false --verbose

echo.
echo 🧪 Executando testes de integracao end-to-end...
call npm test -- --testPathPattern=RAGIntegration.test.js --watchAll=false --verbose

echo.
echo 📊 Executando todos os testes com cobertura...
call npm test -- --watchAll=false --coverage --coverageDirectory=coverage/integration

echo.
echo ✅ Testes de integracao concluidos!
echo 📋 Relatorio de cobertura disponivel em: coverage/integration/

pause