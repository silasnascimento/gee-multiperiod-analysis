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

## Pré-requisitos
- Python 3.8 ou superior
- Conta no Google Earth Engine (GEE) com projeto configurado
- Navegador moderno para rodar o frontend (ex.: Chrome, Firefox)

## Utilização

Siga as instruções para instalar todos os requisitos

## Endpoints
- /calculate_ndvi (POST): Retorna estatísticas NDVI (média, mínimo, máximo) para cada período.
    
    - Entrada: { "roi": GeoJSON, "start_date_period_1": "YYYY-MM-DD", "end_date_period_1": "YYYY-MM-DD", ... }
        
    - Saída: { "period_1": { "ndvi_mean": 0.5, "ndvi_min": 0.2, "ndvi_max": 0.8 }, ... }
        
- /get_ndvi_tiles (POST): Retorna URLs de tiles NDVI para visualização.
    
    - Entrada: Similar ao /calculate_ndvi.
        
    - Saída: { "period_1": { "tile_url": "https://..." }, ... }
        
- /get_image_tile (POST): Retorna URLs de tiles RGB para visualização.
    
    - Entrada: Similar ao /calculate_ndvi.
        
    - Saída: { "period_1": { "tile_url": "https://..." }, ... }



