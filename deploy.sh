#!/bin/bash
# deploy.sh - Deploy portável com Docker Volume
# Uso: ./deploy.sh [PROJECT_ID] [CREDENTIALS_PATH]

set -e

# Configurações padrão
DEFAULT_PROJECT_ID="ee-silasnascimento"
DEFAULT_CREDENTIALS_PATH="/root/documents/credentials"
CONTAINER_NAME="appgee-flask"
IMAGE_NAME="silasnascimento/ndvi-flask-app:latest"
PORT="5000"

# Parâmetros
PROJECT_ID=${1:-$DEFAULT_PROJECT_ID}
CREDENTIALS_PATH=${2:-$DEFAULT_CREDENTIALS_PATH}
VOLUME_NAME="gee-credentials-$(echo $PROJECT_ID | tr -d 'ee-')"

echo "🚀 NDVI Flask App - Deploy Portável"
echo "=================================="
echo "📋 Configurações:"
echo "   Projeto GEE: $PROJECT_ID"
echo "   Credenciais: $CREDENTIALS_PATH"
echo "   Volume: $VOLUME_NAME"
echo "   Container: $CONTAINER_NAME"
echo "   Porta: $PORT"
echo ""

# Verificar se credenciais existem
if [ ! -f "$CREDENTIALS_PATH" ]; then
    echo "❌ Erro: Arquivo de credenciais não encontrado: $CREDENTIALS_PATH"
    echo ""
    echo "💡 Dicas:"
    echo "   1. Execute: earthengine authenticate"
    echo "   2. Ou especifique o caminho: ./deploy.sh $PROJECT_ID /caminho/para/credentials"
    exit 1
fi

# Parar e remover container existente se existir
if docker ps -a --format 'table {{.Names}}' | grep -q "^$CONTAINER_NAME$"; then
    echo "🛑 Parando container existente..."
    docker stop $CONTAINER_NAME 2>/dev/null || true
    docker rm $CONTAINER_NAME 2>/dev/null || true
fi

# Criar volume se não existir
echo "📦 Criando volume Docker: $VOLUME_NAME"
docker volume create $VOLUME_NAME 2>/dev/null || echo "   Volume já existe"

# Copiar credenciais para o volume
echo "🔐 Copiando credenciais para o volume..."
docker run --rm \
    -v $VOLUME_NAME:/data \
    -v "$(dirname $CREDENTIALS_PATH)":/source \
    alpine sh -c "cp /source/$(basename $CREDENTIALS_PATH) /data/credentials && chmod 600 /data/credentials"

# Verificar se a cópia foi bem-sucedida
if ! docker run --rm -v $VOLUME_NAME:/data alpine test -f /data/credentials; then
    echo "❌ Erro: Falha ao copiar credenciais para o volume"
    exit 1
fi

echo "✅ Credenciais copiadas com sucesso"

# Iniciar container
echo "🐳 Iniciando container..."
docker run -d \
    --name $CONTAINER_NAME \
    -v $VOLUME_NAME:/root/.config/earthengine/credentials:ro \
    -p $PORT:5000 \
    -e GEE_PROJECT=$PROJECT_ID \
    --restart unless-stopped \
    $IMAGE_NAME

# Aguardar container inicializar
echo "⏳ Aguardando inicialização..."
sleep 5

# Verificar se container está rodando
if ! docker ps --format 'table {{.Names}}' | grep -q "^$CONTAINER_NAME$"; then
    echo "❌ Erro: Container não iniciou corretamente"
    echo "📋 Logs do container:"
    docker logs $CONTAINER_NAME
    exit 1
fi

# Testar health check
echo "🔍 Testando aplicação..."
if curl -s -f http://localhost:$PORT/health > /dev/null; then
    echo "✅ Aplicação funcionando corretamente!"
    echo ""
    echo "🌐 Aplicação disponível em: http://localhost:$PORT"
    echo "💚 Health check: http://localhost:$PORT/health"
    echo ""
    echo "📋 Comandos úteis:"
    echo "   Ver logs: docker logs $CONTAINER_NAME"
    echo "   Parar: docker stop $CONTAINER_NAME"
    echo "   Iniciar: docker start $CONTAINER_NAME"
    echo "   Remover: docker rm -f $CONTAINER_NAME"
    echo "   Volume: docker volume inspect $VOLUME_NAME"
else
    echo "⚠️ Aplicação iniciada mas health check falhou"
    echo "📋 Logs do container:"
    docker logs $CONTAINER_NAME
fi

echo ""
echo "🎉 Deploy concluído!"
