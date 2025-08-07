# Dockerfile corrigido para suporte a múltiplos projetos GEE
FROM python:3.9-slim

# Definir diretório de trabalho
WORKDIR /app

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements e instalar dependências Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código da aplicação
COPY app.py .

# Criar diretório para credenciais do Earth Engine
RUN mkdir -p /root/.config/earthengine

# Definir variáveis de ambiente padrão
ENV GEE_PROJECT=ee-silasnascimento
ENV FLASK_ENV=production
ENV PYTHONUNBUFFERED=1

# Expor porta
EXPOSE 5000

# Comando para executar a aplicação
CMD ["python", "app.py"]