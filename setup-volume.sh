#!/bin/bash
# setup-volume.sh - Configurar volume Docker com credenciais
# Uso: ./setup-volume.sh [PROJECT_ID] [CREDENTIALS_PATH]

set -e

# Configurações padrão
DEFAULT_PROJECT_ID="ee-silasnascimento"
DEFAULT_CREDENTIALS_PATH="/root/documents/credentials"

# Parâmetros
PROJECT_ID=${1:-$DEFAULT_PROJECT_ID}
CREDENTIALS_PATH=${2:-$DEFAULT_CREDENTIALS_PATH}
VOLUME_NAME="gee-credentials-$(echo $PROJECT_ID | tr -d 'ee-')"

echo "🔧 Configuração de Volume Docker para GEE"
echo "========================================"
echo "📋 Configurações:"
echo "   Projeto GEE: $PROJECT_ID"
echo "   Credenciais: $CREDENTIALS_PATH"
echo "   Volume: $VOLUME_NAME"
echo ""

# Verificar se credenciais existem
if [ ! -f "$CREDENTIALS_PATH" ]; then
    echo "❌ Erro: Arquivo de credenciais não encontrado: $CREDENTIALS_PATH"
    echo ""
    echo "💡 Para obter credenciais:"
    echo "   1. Execute: earthengine authenticate"
    echo "   2. Ou especifique o caminho: ./setup-volume.sh $PROJECT_ID /caminho/para/credentials"
    exit 1
fi

# Criar volume
echo "📦 Criando volume Docker: $VOLUME_NAME"
if docker volume create $VOLUME_NAME 2>/dev/null; then
    echo "✅ Volume criado com sucesso"
else
    echo "ℹ️ Volume já existe"
fi

# Copiar credenciais
echo "🔐 Copiando credenciais para o volume..."
docker run --rm \
    -v $VOLUME_NAME:/data \
    -v "$(dirname $CREDENTIALS_PATH)":/source \
    alpine sh -c "cp /source/$(basename $CREDENTIALS_PATH) /data/credentials && chmod 600 /data/credentials"

# Verificar cópia
if docker run --rm -v $VOLUME_NAME:/data alpine test -f /data/credentials; then
    echo "✅ Credenciais copiadas com sucesso"
else
    echo "❌ Erro: Falha ao copiar credenciais"
    exit 1
fi

# Mostrar informações do volume
echo ""
echo "📋 Informações do Volume:"
docker volume inspect $VOLUME_NAME

echo ""
echo "🎉 Volume configurado com sucesso!"
echo ""
echo "💡 Próximos passos:"
echo "   1. Execute: ./deploy.sh $PROJECT_ID"
echo "   2. Ou use Docker Compose: docker-compose up -d"
echo "   3. Ou comando manual:"
echo "      docker run -d --name appgee-flask \\"
echo "        -v $VOLUME_NAME:/root/.config/earthengine/credentials:ro \\"
echo "        -p 5000:5000 \\"
echo "        -e GEE_PROJECT=$PROJECT_ID \\"
echo "        silasnascimento/ndvi-flask-app:latest"
