#!/bin/bash

echo "🔧 Script para corrigir autenticação do Google Earth Engine"
echo "=========================================================="

# Parar container atual
echo "🛑 Parando container atual..."
docker stop appgee-flask 2>/dev/null || true
docker rm appgee-flask 2>/dev/null || true

# Remover volume antigo se existir
echo "🗑️  Removendo volume antigo..."
docker volume rm earthengine 2>/dev/null || true

# Construir nova imagem
echo "🏗️  Construindo nova imagem..."
docker build -f Dockerfile.fixed -t ndvi-flask-app:fixed .

# Executar novo container
echo "🚀 Iniciando novo container..."
docker-compose -f docker-compose.fixed.yml up -d

# Aguardar container inicializar
echo "⏳ Aguardando container inicializar..."
sleep 10

# Verificar status
echo "📊 Verificando status do container..."
docker ps | grep appgee-flask

echo ""
echo "🔐 Para autenticar o Google Earth Engine, execute:"
echo "   docker exec -it appgee-flask earthengine authenticate"
echo ""
echo "📋 Ou use o método Python:"
echo "   docker exec -it appgee-flask python -c \"import ee; ee.Authenticate()\""
echo ""
echo "🧪 Para testar a aplicação:"
echo "   curl http://localhost:5000/health"
echo ""
echo "✅ Script concluído!"
