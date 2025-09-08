# NDVI Flask Docker Application

🌍 **Aplicação Flask containerizada para análise NDVI e dados climáticos usando Google Earth Engine**

[![Docker](https://img.shields.io/badge/Docker-Ready-blue?logo=docker)](https://www.docker.com/)
[![Python](https://img.shields.io/badge/Python-3.9+-green?logo=python)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-2.0+-red?logo=flask)](https://flask.palletsprojects.com/)
[![Google Earth Engine](https://img.shields.io/badge/Google%20Earth%20Engine-API-orange)](https://earthengine.google.com/)

## 📋 Visão Geral

Esta aplicação Flask fornece uma API REST para análise de dados de sensoriamento remoto e climáticos através do Google Earth Engine. Suporta múltiplos projetos GEE e oferece endpoints otimizados para análise NDVI e estatísticas climáticas.

### 🎯 Principais Funcionalidades

- **Análise NDVI**: Cálculo de índices de vegetação usando Sentinel-2 e Landsat 9
- **Dados Climáticos**: Estatísticas de precipitação (CHIRPS) e temperatura (ERA5-Land)
- **Múltiplos Projetos**: Suporte a diferentes projetos Google Earth Engine
- **Duas Soluções de Deploy**: Portável e Corrigida para máxima flexibilidade
- **Containerização**: Deploy simplificado com Docker e volumes nomeados
- **API Otimizada**: Processamento paralelo e cache inteligente
- **Monitoramento**: Endpoint de saúde e logs detalhados
- **Segurança**: Credenciais em volumes Docker read-only
- **Autenticação GEE**: Verificação automática e inicialização inteligente



## 🛰️ Datasets Utilizados

### Sensoriamento Remoto
- **[Sentinel-2 MSI](https://developers.google.com/earth-engine/datasets/catalog/COPERNICUS_S2_SR_HARMONIZED)**: Resolução 10m, análise NDVI principal
- **[Landsat 9 OLI](https://developers.google.com/earth-engine/datasets/catalog/LANDSAT_LC09_C02_T1_L2)**: Resolução 30m, fallback para NDVI

### Dados Climáticos
- **[CHIRPS Daily](https://developers.google.com/earth-engine/datasets/catalog/UCSB-CHG_CHIRPS_DAILY)**: Precipitação diária (~5.5km)
- **[ERA5-Land](https://developers.google.com/earth-engine/datasets/catalog/ECMWF_ERA5_LAND_HOURLY)**: Temperatura 2m (~11km)

## 🔧 Tecnologias

- **Backend**: Flask 2.0+ com CORS
- **Processamento**: Google Earth Engine Python API
- **Containerização**: Docker
- **Concorrência**: ThreadPoolExecutor para processamento paralelo
- **Otimização**: Cache LRU e consolidação de operações GEE

## 📊 Endpoints da API

### 🌿 Análise NDVI
```http
POST /ndvi_composite
Content-Type: application/json

{
  "roi": {
    "type": "Polygon",
    "coordinates": [[[-50.1, -27.1], [-50.0, -27.1], [-50.0, -27.0], [-50.1, -27.0], [-50.1, -27.1]]]
  },
  "date_periods": [
    ["2024-01-01", "2024-01-31"],
    ["2024-02-01", "2024-02-29"]
  ]
}
```

### 🌡️ Dados Climáticos
```http
POST /climate_stats
Content-Type: application/json

{
  "point": {
    "type": "Point",
    "coordinates": [-50.667, -27.819]
  },
  "date_periods": [
    ["2025-01-15", "2025-02-15"],
    ["2025-02-15", "2025-03-15"]
  ]
}
```

### 💚 Saúde da Aplicação
```http
GET /health
```

**Resposta:**
```json
{
  "status": "healthy",
  "gee_project": {
    "project_id": "ee-meu-projeto",
    "status": "initialized",
    "source": "environment_variable"
  },
  "timestamp": 1704567890.123
}
```


## 🚀 Instalação e Configuração

### Pré-requisitos

1. **Docker** instalado
2. **Credenciais Google Earth Engine** configuradas
3. **Projeto GEE** com acesso aos datasets necessários

## 🎯 **Duas Soluções de Deploy Disponíveis**

### **Solução 1: Deploy Portável** ⭐ (Recomendado para Produção)

**Deploy em qualquer VPS com apenas 3 comandos:**

```bash
# 1. Clonar repositório
git clone <seu-repositorio>
cd ndvi-multiperiod-webgis

# 2. Obter credenciais GEE
earthengine authenticate

# 3. Deploy automático
chmod +x *.sh
./deploy.sh
```

**Com projeto personalizado:**
```bash
./deploy.sh ee-meu-projeto
```

**Com credenciais em local específico:**
```bash
./deploy.sh ee-meu-projeto /caminho/para/credentials
```

### **Solução 2: Deploy Corrigido** ⭐ (Recomendado para Desenvolvimento)

**Deploy com container otimizado e autenticação automática:**

```bash
# 1. Clonar repositório
git clone <seu-repositorio>
cd ndvi-multiperiod-webgis

# 2. Deploy com container corrigido
chmod +x fix-gee-auth.sh
./fix-gee-auth.sh

# 3. Verificar status
curl http://localhost:5000/health
```

**Ou usando Docker Compose:**
```bash
docker-compose -f docker-compose.fixed.yml up -d
```

### 📦 Opção 1: Docker Hub (Método Antigo)

```bash
# ⚠️ MÉTODO ANTIGO - Dependente da VPS
docker run -d --name ndvi-flask \
  -v /caminho/para/credentials:/root/.config/earthengine/credentials \
  -p 5000:5000 \
  -e GEE_PROJECT=seu-projeto-gee \
  silasnascimento/ndvi-flask-app:latest
```

### 🔨 Opção 2: Build Local

```bash
# Clonar repositório
git clone https://github.com/silasnascimento/ndvi-flask-docker.git
cd ndvi-flask-docker

# Build da imagem
docker build -t silasnascimento/ndvi-flask-app .

# Deploy com script automatizado
./deploy.sh
```

### ⚙️ Configuração de Credenciais GEE

#### Método 1: Autenticação Interativa
```bash
# No host
earthengine authenticate

# Localizar arquivo de credenciais
ls ~/.config/earthengine/
```

#### Método 2: Service Account
```bash
# Criar service account no Google Cloud Console
# Baixar chave JSON
# Configurar variável de ambiente
export GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json
```

### 📁 Arquivos do Projeto

| Arquivo | Descrição | Solução |
|---------|-----------|---------|
| `app.py` | Aplicação Flask principal | Ambas |
| `requirements.txt` | Dependências Python | Ambas |
| **Solução 1 - Deploy Portável** | | |
| `deploy.sh` | **Script de deploy portável** | 1 |
| `setup-volume.sh` | Configuração de volume Docker | 1 |
| `docker-compose.yml` | Deploy com Docker Compose | 1 |
| `DEPLOY.md` | **Guia completo de deploy** | 1 |
| `env.example` | Exemplo de variáveis de ambiente | 1 |
| **Solução 2 - Deploy Corrigido** | | |
| `Dockerfile.fixed` | **Dockerfile otimizado** | 2 |
| `docker-compose.fixed.yml` | **Configuração corrigida** | 2 |
| `entrypoint.sh` | **Script de inicialização** | 2 |
| `fix-gee-auth.sh` | **Script de correção automática** | 2 |
| `SOLUCAO_IMPLEMENTADA.md` | **Documentação da solução** | 2 |
| **Arquivos Originais** | | |
| `Dockerfile` | Dockerfile original | Original |
| `README.md` | Documentação principal | Ambas |

### 🌐 Variáveis de Ambiente

| Variável | Descrição | Padrão | Obrigatório |
|----------|-----------|---------|-------------|
| `GEE_PROJECT` | ID do projeto Google Earth Engine | `ee-silasnascimento` | ❌ |
| `FLASK_ENV` | Ambiente Flask | `production` | ❌ |
| `PYTHONUNBUFFERED` | Logs em tempo real | `1` | ❌ |


## 📖 Exemplos de Uso

### 🌿 Análise NDVI para Área Agrícola

```bash
curl -X POST http://localhost:5000/ndvi_composite \
  -H "Content-Type: application/json" \
  -d '{
    "roi": {
      "type": "Polygon",
      "coordinates": [[[-50.1, -27.1], [-50.0, -27.1], [-50.0, -27.0], [-50.1, -27.0], [-50.1, -27.1]]]
    },
    "date_periods": [
      ["2024-01-01", "2024-01-31"],
      ["2024-02-01", "2024-02-29"]
    ]
  }'
```

**Resposta:**
```json
{
  "ndvi": {
    "period_1": {
      "ndvi_mean": 0.65,
      "ndvi_min": 0.12,
      "ndvi_max": 0.89,
      "satellite": "sentinel"
    },
    "period_2": {
      "ndvi_mean": 0.71,
      "ndvi_min": 0.18,
      "ndvi_max": 0.92,
      "satellite": "sentinel"
    }
  },
  "ndvi_tiles": {
    "period_1": {
      "tile_url": "https://earthengine.googleapis.com/...",
      "satellite": "sentinel"
    }
  },
  "project_info": {
    "project_id": "ee-meu-projeto",
    "status": "initialized",
    "source": "environment_variable"
  }
}
```

### 🌡️ Estatísticas Climáticas para Ponto

```bash
curl -X POST http://localhost:5000/climate_stats \
  -H "Content-Type: application/json" \
  -d '{
    "point": {
      "type": "Point",
      "coordinates": [-50.667, -27.819]
    },
    "date_periods": [
      ["2025-01-15", "2025-02-15"]
    ]
  }'
```

**Resposta:**
```json
{
  "precipitation": {
    "period_1": {
      "precipitation_sum": 156.7,
      "precipitation_daily_mean": 5.1,
      "source": "precipitation"
    }
  },
  "temperature": {
    "period_1": {
      "temperature_min_celsius": 18.2,
      "temperature_mean_celsius": 24.8,
      "temperature_max_celsius": 31.5,
      "source": "temperature"
    }
  },
  "processing_time_seconds": 3.42,
  "project_info": {
    "project_id": "ee-meu-projeto",
    "status": "initialized",
    "source": "environment_variable"
  }
}
```


## 🏭 Deploy em Produção

### 🎯 **Escolha da Solução**

| Cenário | Solução Recomendada | Motivo |
|---------|-------------------|--------|
| **Produção Nova** | **Solução 1** (Portável) | Deploy em 3 comandos, totalmente portável |
| **Desenvolvimento** | **Solução 2** (Corrigida) | Autenticação automática, logs detalhados |
| **Migração** | **Solução 1** (Portável) | Migração fácil entre VPS |
| **Testes** | **Solução 2** (Corrigida) | Setup rápido, debugging facilitado |

### **Solução 1: Deploy Portável** (Produção)

```bash
# Deploy completo com um comando
./deploy.sh ee-meu-projeto-prod

# Verificar status
curl http://localhost:5000/health
```

**Configurar volume primeiro:**
```bash
./setup-volume.sh ee-meu-projeto-prod
```

**Deploy com Docker Compose:**
```bash
# Usar o docker-compose.yml incluído
docker-compose up -d
```

### **Solução 2: Deploy Corrigido** (Desenvolvimento)

```bash
# Deploy com container otimizado
./fix-gee-auth.sh

# Verificar status
curl http://localhost:5000/health
```

**Deploy com Docker Compose:**
```bash
docker-compose -f docker-compose.fixed.yml up -d
```

**Ou com configuração personalizada:**
```yaml
# docker-compose.yml
version: '3.8'

services:
  ndvi-flask:
    image: silasnascimento/ndvi-flask-app:latest
    container_name: ndvi-flask-prod
    restart: unless-stopped
    ports:
      - "5000:5000"
    volumes:
      - gee-credentials-meuprojeto:/root/.config/earthengine/credentials:ro
    environment:
      - GEE_PROJECT=ee-meu-projeto-prod
      - FLASK_ENV=production
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

volumes:
  gee-credentials-meuprojeto:
    external: true
```

### 🌐 Configuração Nginx

```nginx
# nginx.conf
events {
    worker_connections 1024;
}

http {
    upstream flask_app {
        server ndvi-flask:5000;
    }

    server {
        listen 80;
        server_name seu-dominio.com;
        return 301 https://$server_name$request_uri;
    }

    server {
        listen 443 ssl;
        server_name seu-dominio.com;

        ssl_certificate /etc/nginx/ssl/cert.pem;
        ssl_certificate_key /etc/nginx/ssl/key.pem;

        location / {
            proxy_pass http://flask_app;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            proxy_read_timeout 300s;
            proxy_connect_timeout 75s;
        }

        location /health {
            proxy_pass http://flask_app/health;
            access_log off;
        }
    }
}
```

### 🔒 SSL com Let's Encrypt

```bash
# Instalar Certbot
sudo apt install certbot python3-certbot-nginx

# Obter certificado
sudo certbot --nginx -d seu-dominio.com

# Renovação automática
sudo crontab -e
# Adicionar: 0 12 * * * /usr/bin/certbot renew --quiet
```

## 🎯 **Comparação das Soluções**

### ✅ **Evolução do Projeto**

| Aspecto | Método Original | **Solução 1** (Portável) | **Solução 2** (Corrigida) |
|---------|----------------|---------------------------|----------------------------|
| **Portabilidade** | ❌ Dependente da VPS | ✅ **Totalmente portável** | ✅ **Portável** |
| **Segurança** | ⚠️ Caminho exposto | ✅ **Volume read-only** | ✅ **Volume isolado** |
| **Facilidade** | ❌ Comando complexo | ✅ **3 comandos** | ✅ **1 comando** |
| **Autenticação** | ❌ Manual | ✅ **Automática** | ✅ **Verificação automática** |
| **Debugging** | ❌ Limitado | ✅ **Logs básicos** | ✅ **Logs detalhados** |
| **Deploy** | ❌ 5+ comandos | ✅ **3 comandos** | ✅ **1 comando** |
| **Uso Recomendado** | ❌ Não recomendado | ✅ **Produção** | ✅ **Desenvolvimento** |

### 🚀 **Benefícios das Soluções**

#### **Solução 1 - Deploy Portável**
- **🎯 Deploy em 3 comandos**: Clone → Authenticate → Deploy
- **🔒 Segurança**: Credenciais em volumes Docker read-only
- **📦 Portabilidade**: Funciona em qualquer VPS com Docker
- **🛠️ Manutenção**: Scripts automatizados para todas as operações
- **📋 Documentação**: Guia completo em `DEPLOY.md`
- **🔄 Backup**: Volumes Docker podem ser facilmente copiados

#### **Solução 2 - Deploy Corrigido**
- **⚡ Setup rápido**: Um comando para deploy completo
- **🔍 Debugging**: Logs detalhados e verificação automática
- **🛡️ Autenticação**: Verificação automática de credenciais GEE
- **🔧 Manutenção**: Scripts de correção automática
- **📊 Monitoramento**: Health checks e logs estruturados
- **🚀 Desenvolvimento**: Ideal para testes e desenvolvimento

## 🔐 **Estado Atual das Credenciais**

### **Container Ativo**
- **Container**: `appgee-flask` (Solução 2)
- **Volume Docker**: `earthengine_credentials`
- **Caminho no Container**: `/root/.config/earthengine/credentials`
- **Caminho no Host**: `/var/lib/docker/volumes/earthengine_credentials/_data/credentials`

### **Arquivo Original**
- **Caminho Original**: `/root/documents/credentials` ✅ **Preservado**
- **Status**: Arquivo original mantido e copiado para volume Docker
- **Integridade**: ✅ **Arquivos idênticos** (mesmo hash MD5)

### **Volumes Disponíveis**
```bash
# Listar volumes de credenciais
docker volume ls | grep credentials

# Resultado:
# local     earthengine_credentials      (Solução 2 - Ativo)
# local     gee-credentials-silasnascimnto (Solução 1 - Disponível)
```

### 📖 **Documentação Adicional**

Para informações detalhadas sobre cada solução, consulte:
- **[DEPLOY.md](DEPLOY.md)** - Guia completo de deploy portável (Solução 1)
- **[SOLUCAO_IMPLEMENTADA.md](SOLUCAO_IMPLEMENTADA.md)** - Documentação da solução corrigida (Solução 2)
- **[docs/setup.md](docs/setup.md)** - Configuração manual (método original)

