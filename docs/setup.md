# Guia de Configuração: NDVI Multi-Period WebGIS

Este guia detalha os passos para configurar o ambiente necessário para rodar a API Flask integrada ao Google Earth Engine (GEE) no Ubuntu Server, utilizada no projeto NDVI Multi-Period WebGIS.

## Pré-requisitos
- **Conta Google**: Com acesso ao Google Earth Engine.
- **Projeto Earth Engine**: Com as APIs do Earth Engine habilitadas.
- **Ubuntu Server**: Com acesso SSH.

## 1. Acesso ao servidor
Conecte-se ao seu servidor Ubuntu via SSH.

## 2. Instalação do Python 3 e pip
```bash
sudo apt update
sudo apt install python3 python3-pip
```
3. Criação do ambiente virtual
```bash

python3 -m venv .venv
source .venv/bin/activate  # Ativa o ambiente virtual (note o espaço antes de .venv)
```
4. Instalação das bibliotecas Python
```bash

pip install flask flask-cors earthengine-api
```
5. Instalação do Google Cloud SDK
```bash

# Instale o curl
sudo apt install curl -y

# Baixe o script de instalação
curl https://sdk.cloud.google.com | bash

# Reinicie o terminal ou execute
exec -l $SHELL

# Para adicionar permanentemente, inclua no seu .bashrc/.zshrc:
echo 'source ~/google-cloud-sdk/path.bash.inc' >> ~/.bashrc

# Inicialize o SDK e siga as instruções
gcloud init

Importante: Durante a instalação, escolha a opção para instalar o Google Cloud SDK no ambiente virtual atual.
```
6. Inicialização do Google Cloud SDK
```bash

source ~/google-cloud-sdk/path.bash.inc  # Ajuste o caminho conforme a instalação
gcloud components update
```
7. Autenticação no Earth Engine
```bash

earthengine authenticate

Siga as instruções na tela para fazer login na sua conta Google e autorizar o acesso ao Earth Engine.
```
8. Configuração do Firewall (UFW)
```bash

sudo ufw allow 5000

Se necessário, ajuste a regra para restringir o acesso a determinados IPs ou redes.
```
9. Criação do grupo de segurança na instância EC2
No AWS Console > EC2 > Security Groups:
Adicione uma regra de entrada (Inbound Rule) para a porta 5000:
Type: Custom TCP

Port Range: 5000

Source: 0.0.0.0/0 (ou seu IP específico).

10. Execução da API
```bash

python app.py
```
A API estará disponível na porta 5000.

11. Testando a API
Utilize uma ferramenta como curl ou Postman para enviar requisições para as rotas da API e verificar se estão funcionando corretamente.

12. Instalando o SSL e habilitando HTTPS
Para habilitar HTTPS no Flask, siga estes passos:
Gerar certificados SSL:
Use openssl para criar certificados autoassinados (para teste) ou obtenha certificados válidos (ex.: via Let's Encrypt):
```bash

openssl req -x509 -newkey rsa:2048 -keyout key.pem -out cert.pem -days 365 -nodes

Coloque os arquivos cert.pem e key.pem em um diretório seguro (ex.: ssl/).
```
Configurar o Flask:
No app.py, ajuste o app.run() para usar SSL:
```python

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False, ssl_context=('/caminho/para/ssl/cert.pem', '/caminho/para/ssl/key.pem'))
```
Atualize o caminho para os certificados conforme o local onde você os salvou.

Reiniciar a API:
Após configurar, reinicie a API com python app.py.

