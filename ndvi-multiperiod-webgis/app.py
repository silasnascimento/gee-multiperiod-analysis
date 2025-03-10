from flask import Flask, request, jsonify
from flask_cors import CORS
import ee

# Inicializa o GEE (movido para uma função para robustez)
def initialize_gee():
    try:
        ee.Initialize(project="ee-silasnascimento")
    except Exception as e:
        raise Exception(f"Erro ao inicializar o Google Earth Engine: {str(e)}")

app = Flask(__name__)
CORS(app)  # Habilita CORS

# Função para aplicar a máscara de nuvens (atualizada para nuvens cirrus e opacas)
def apply_cloud_mask(image):
    qa = image.select('QA60')
    cloud_mask = qa.bitwiseAnd(1 << 10).eq(0).And(qa.bitwiseAnd(1 << 11).eq(0))  # Bits 10 e 11
    return image.updateMask(cloud_mask)

# Função auxiliar para extrair períodos de datas do JSON
def extract_date_periods(data):
    periods = {}
    i = 1
    while True:
        start_key = f'start_date_period_{i}'
        end_key = f'end_date_period_{i}'
        if start_key in data and end_key in data:
            periods[f'period_{i}'] = {
                'start_date': data[start_key],
                'end_date': data[end_key]
            }
            i += 1
        else:
            break
    # Caso não haja períodos numerados, usa valores padrão únicos
    if not periods and 'start_date' in data and 'end_date' in data:
        periods['period_1'] = {
            'start_date': data['start_date'],
            'end_date': data['end_date']
        }
    return periods if periods else {'period_1': {'start_date': '2024-01-01', 'end_date': '2024-01-28'}}

# Rota para calcular a média do NDVI para múltiplos períodos
@app.route('/calculate_ndvi', methods=['POST'])
def calculate_ndvi():
    try:
        initialize_gee()  # Garante inicialização do GEE
        data = request.json
        if not data or 'roi' not in data or 'coordinates' not in data['roi']:
            return jsonify({'error': 'GeoJSON de ROI inválido'}), 400
        
        roi = ee.Geometry.Polygon(data['roi']['coordinates'])
        periods = extract_date_periods(data)
        results = {}

        for period_name, dates in periods.items():
            start_date = dates['start_date']
            end_date = dates['end_date']

            # Filtra a coleção de imagens e aplica a máscara de nuvens
            collection = (ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED")
                          .filterDate(start_date, end_date)
                          .filterBounds(roi)
                          .map(apply_cloud_mask))

            # Calcula o NDVI
            ndvi = (collection.median()
                    .normalizedDifference(['B8', 'B4'])
                    .rename('NDVI')
                    .clip(roi))

            # Calcula estatísticas de NDVI
            stats = ndvi.reduceRegion(
                reducer=ee.Reducer.mean().combine(reducer2=ee.Reducer.minMax(), sharedInputs=True),
                geometry=roi,
                scale=10,
                maxPixels=1e6
            )

            # Obtém os valores em uma única chamada
            stats_dict = stats.getInfo()
            results[period_name] = {
                'ndvi_mean': stats_dict.get('NDVI_mean'),
                'ndvi_min': stats_dict.get('NDVI_min'),
                'ndvi_max': stats_dict.get('NDVI_max')
            }

        return jsonify(results)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Rota para obter tiles do NDVI para múltiplos períodos
@app.route('/get_ndvi_tiles', methods=['POST'])
def get_ndvi_tiles():
    try:
        initialize_gee()
        data = request.json
        if not data or 'roi' not in data or 'coordinates' not in data['roi']:
            return jsonify({'error': 'GeoJSON de ROI inválido'}), 400
        
        roi = ee.Geometry.Polygon(data['roi']['coordinates'])
        periods = extract_date_periods(data)
        vis_params = data.get('vis_params', {'min': 0, 'max': 0.8, 'palette': ['red', 'yellow', 'green']})
        results = {}

        for period_name, dates in periods.items():
            start_date = dates['start_date']
            end_date = dates['end_date']

            # Filtra a coleção de imagens e aplica a máscara de nuvens
            collection = (ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED")
                          .filterBounds(roi)
                          .filterDate(start_date, end_date)
                          .map(apply_cloud_mask))

            # Calcula o NDVI
            ndvi = (collection.median()
                    .normalizedDifference(['B8', 'B4'])
                    .rename('NDVI')
                    .clip(roi))

            # Gera o mapa NDVI como tiles
            map_id_dict = ndvi.getMapId(vis_params)
            results[period_name] = {
                'tile_url': map_id_dict['tile_fetcher'].url_format
            }

        return jsonify(results)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Rota para obter tiles da imagem RGB para múltiplos períodos
@app.route('/get_image_tile', methods=['POST'])
def get_image_tile():
    try:
        initialize_gee()
        data = request.json
        if not data or 'roi' not in data or 'coordinates' not in data['roi']:
            return jsonify({'error': 'GeoJSON de ROI inválido'}), 400
        
        roi = ee.Geometry.Polygon(data['roi']['coordinates'])
        periods = extract_date_periods(data)
        vis_params = data.get('vis_params', {'bands': ['B4', 'B3', 'B2'], 'min': 0, 'max': 3000})
        results = {}

        for period_name, dates in periods.items():
            start_date = dates['start_date']
            end_date = dates['end_date']

            # Filtra a coleção de imagens e aplica a máscara de nuvens
            collection = (ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED")
                          .filterBounds(roi)
                          .filterDate(start_date, end_date)
                          .map(apply_cloud_mask))

            # Obtém a primeira imagem da coleção
            img = collection.first().clip(roi)

            # Gera o mapa como tiles
            map_id_dict = img.getMapId(vis_params)
            results[period_name] = {
                'tile_url': map_id_dict['tile_fetcher'].url_format
            }

        return jsonify(results)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False, ssl_context=('/home/silasogeo/ssl/cert.pem', '/home/silasogeo/ssl/key.pem'))