#!/bin/bash
set -e

echo "🚀 Iniciando container NDVI Flask App..."

# Verificar se as credenciais do GEE existem
if [ ! -f "/root/.config/earthengine/credentials" ]; then
    echo "❌ Credenciais do Google Earth Engine não encontradas!"
    echo "📋 Para autenticar, execute:"
    echo "   docker exec -it appgee-flask earthengine authenticate"
    echo "   ou"
    echo "   docker exec -it appgee-flask python -c \"import ee; ee.Authenticate()\""
    echo ""
    echo "⚠️  Continuando sem autenticação GEE..."
else
    echo "✅ Credenciais do GEE encontradas"
    
    # Testar autenticação
    echo "🔍 Testando autenticação GEE..."
    python -c "
import ee
try:
    ee.Initialize(project='$GEE_PROJECT')
    print('✅ GEE autenticado com sucesso!')
    # Teste simples
    result = ee.Number(1).getInfo()
    print(f'✅ Teste de conectividade: {result}')
except Exception as e:
    print(f'❌ Erro na autenticação GEE: {e}')
    print('⚠️  Continuando sem autenticação GEE...')
"
fi

echo "🌐 Iniciando aplicação Flask..."
exec python app.py
