# 🚀 Guia de Deploy Portável - NDVI Flask App

## 📋 Visão Geral

Este guia mostra como fazer deploy da aplicação NDVI Flask App de forma **completamente portável**, sem depender de caminhos específicos da VPS.

## 🎯 Problema Resolvido

**Antes (Dependente da VPS):**
```bash
# ❌ Dependia do caminho específico da VPS
docker run -d --name appgee-flask \
  -v /root/documents/credentials:/root/.config/earthengine/credentials \
  -p 5000:5000 \
  -e GEE_PROJECT=ee-silasnascimento \
  silasnascimento/ndvi-flask-app:latest
```

**Depois (Portável):**
```bash
# ✅ Usa volume Docker nomeado - funciona em qualquer VPS
./deploy.sh
```

## 🛠️ Arquivos Criados

- `deploy.sh` - Script principal de deploy
- `setup-volume.sh` - Configuração do volume Docker
- `docker-compose.yml` - Deploy com Docker Compose
- `env.example` - Exemplo de variáveis de ambiente

## 🚀 Métodos de Deploy

### **Método 1: Script Automatizado (Recomendado)**

```bash
# Deploy completo com um comando
./deploy.sh

# Com projeto personalizado
./deploy.sh ee-meu-projeto

# Com credenciais em local específico
./deploy.sh ee-meu-projeto /caminho/para/credentials
```

### **Método 2: Docker Compose**

```bash
# Configurar volume primeiro
./setup-volume.sh

# Deploy com Docker Compose
docker-compose up -d
```

### **Método 3: Comando Manual**

```bash
# 1. Configurar volume
./setup-volume.sh

# 2. Executar container
docker run -d --name appgee-flask \
  -v gee-credentials-silasnascimnto:/root/.config/earthengine/credentials:ro \
  -p 5000:5000 \
  -e GEE_PROJECT=ee-silasnascimento \
  silasnascimento/ndvi-flask-app:latest
```

## 🔧 Configuração Inicial

### **1. Obter Credenciais GEE**

```bash
# Autenticar no Google Earth Engine
earthengine authenticate

# Verificar se credenciais foram criadas
ls ~/.config/earthengine/credentials
```

### **2. Configurar Volume (Primeira vez)**

```bash
# Configurar volume com credenciais
./setup-volume.sh

# Ou com projeto personalizado
./setup-volume.sh ee-meu-projeto /caminho/para/credentials
```

### **3. Deploy**

```bash
# Deploy automático
./deploy.sh
```

## 📦 Gerenciamento de Volumes

### **Listar Volumes**
```bash
docker volume ls | grep gee-credentials
```

### **Inspecionar Volume**
```bash
docker volume inspect gee-credentials-silasnascimnto
```

### **Remover Volume**
```bash
docker volume rm gee-credentials-silasnascimnto
```

### **Backup do Volume**
```bash
# Criar backup
docker run --rm -v gee-credentials-silasnascimnto:/data -v $(pwd):/backup alpine tar czf /backup/gee-credentials-backup.tar.gz -C /data .

# Restaurar backup
docker run --rm -v gee-credentials-silasnascimnto:/data -v $(pwd):/backup alpine tar xzf /backup/gee-credentials-backup.tar.gz -C /data
```

## 🌐 Deploy em Nova VPS

### **Passo a Passo Completo**

1. **Clonar repositório**
```bash
git clone <seu-repositorio>
cd ndvi-multiperiod-webgis
```

2. **Obter credenciais GEE**
```bash
earthengine authenticate
```

3. **Deploy automático**
```bash
chmod +x *.sh
./deploy.sh
```

4. **Verificar funcionamento**
```bash
curl http://localhost:5000/health
```

## 🔒 Segurança

### **Volume Read-Only**
- Credenciais são montadas como **read-only**
- Container não pode modificar credenciais
- Maior segurança em produção

### **Permissões**
- Credenciais têm permissão 600 (apenas owner)
- Volume isolado do sistema host
- Não exposição de credenciais em logs

## 🐛 Troubleshooting

### **Container não inicia**
```bash
# Ver logs
docker logs appgee-flask

# Verificar volume
docker volume inspect gee-credentials-silasnascimnto
```

### **Credenciais não encontradas**
```bash
# Verificar se arquivo existe
ls -la /root/documents/credentials

# Reconfigurar volume
./setup-volume.sh
```

### **Health check falha**
```bash
# Aguardar inicialização
sleep 30

# Testar manualmente
curl http://localhost:5000/health
```

## 📊 Vantagens da Solução

| Aspecto | Antes | Depois |
|---------|-------|--------|
| **Portabilidade** | ❌ Dependente da VPS | ✅ Funciona em qualquer lugar |
| **Segurança** | ⚠️ Caminho exposto | ✅ Volume isolado |
| **Facilidade** | ❌ Comando complexo | ✅ Um comando simples |
| **Backup** | ❌ Difícil | ✅ Volume Docker |
| **Manutenção** | ❌ Manual | ✅ Scripts automatizados |

## 🎉 Conclusão

A solução implementada torna o deploy **100% portável** e **seguro**, permitindo que qualquer pessoa com credenciais GEE válidas possa fazer deploy da aplicação em sua própria VPS com um simples comando.
