# NDVI Multi-Period WebGIS

![Licença](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.8%2B-blue.svg)
![Leaflet](https://img.shields.io/badge/leaflet-1.7.1-green.svg)

Este projeto é um WebGIS ambiental que permite calcular e visualizar o índice NDVI (Normalized Difference Vegetation Index) para múltiplos períodos de tempo, utilizando o Google Earth Engine (GEE) e o Leaflet. O backend é construído com Flask, e o frontend utiliza Leaflet para exibir mapas interativos, permitindo que o usuário desenhe áreas de interesse e visualize camadas NDVI sobrepostas a basemaps como OpenStreetMap, Google Maps e Esri.

## Funcionalidades
- Desenhar uma área no mapa para calcular o NDVI.
- Suporte a múltiplos períodos de tempo, com nomes personalizáveis no frontend.
- Visualização de camadas NDVI sobre basemaps (OpenStreetMap, Google Maps, Esri).
- Exibição de estatísticas NDVI (média, mínimo, máximo) para cada período.
- Controle de camadas para alternar entre basemaps e camadas NDVI.

## Estrutura do Projeto

ndvi-multiperiod-webgis/
├── app.py              # Backend Flask para processar NDVI com GEE
├── frontend/           # Arquivos do frontend
│   ├── index.html      # Página principal do WebGIS
│   ├── script.js       # Lógica do frontend (Leaflet, requisições)
│   └── styles.css      # Estilos CSS
├── docs/               # Documentação adicional
│   └── setup.md        # Guia de configuração do ambiente
├── requirements.txt    # Dependências do backend
├── README.md           # Documentação principal
├── LICENSE             # Licença (MIT)



## Pré-requisitos
- Python 3.8 ou superior
- Conta no Google Earth Engine (GEE) com projeto configurado
- Navegador moderno para rodar o frontend (ex.: Chrome, Firefox)

## Instalação

### 1. Clone o repositório
```bash
git clone https://github.com/seu-usuario/ndvi-multiperiod-webgis.git
cd ndvi-multiperiod-webgis
```

