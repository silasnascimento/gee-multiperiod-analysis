from concurrent.futures import ThreadPoolExecutor, as_completed
from flask import Flask, request, jsonify
from flask_cors import CORS
import ee
import time
import os

# Inicialização do Google Earth Engine com suporte a variável de ambiente
def initialize_gee():
    try:
        # Usar variável de ambiente GEE_PROJECT ou fallback para projeto padrão
        project_id = os.getenv('GEE_PROJECT', 'ee-silasnascimento')
        
        # Log do projeto sendo usado
        print(f"🌍 Inicializando Google Earth Engine com projeto: {project_id}")
        
        # Inicializar com o projeto especificado
        ee.Initialize(project=project_id)
        
        # Verificar se a inicialização foi bem-sucedida
        try:
            # Teste simples para verificar se a conexão está funcionando
            ee.Number(1).getInfo()
            print(f"✅ GEE inicializado com sucesso - Projeto: {project_id}")
        except Exception as test_error:
            print(f"⚠️ Aviso: GEE inicializado mas teste de conectividade falhou: {test_error}")
            
    except Exception as e:
        error_msg = f"❌ Erro ao inicializar o Google Earth Engine: {str(e)}"
        print(error_msg)
        raise Exception(error_msg)

# Função para obter informações do projeto atual
def get_project_info():
    """Retorna informações sobre o projeto GEE atual."""
    try:
        project_id = os.getenv('GEE_PROJECT', 'ee-silasnascimento')
        return {
            'project_id': project_id,
            'status': 'initialized',
            'source': 'environment_variable' if os.getenv('GEE_PROJECT') else 'default'
        }
    except Exception as e:
        return {
            'project_id': 'unknown',
            'status': 'error',
            'error': str(e)
        }

# Configuração do Flask
app = Flask(__name__)
CORS(app)

# Funções de mascaramento e cobertura de nuvens para Sentinel-2
def get_cloud_coverage_sentinel(image, roi):
    scl = image.select('SCL')
    cloud_mask = scl.eq(8).Or(scl.eq(9)).Or(scl.eq(3))
    cloud_area = cloud_mask.reduceRegion(
        reducer=ee.Reducer.mean(),
        geometry=roi,
        scale=10,
        maxPixels=1e6
    ).get('SCL')
    return image.set('cloud_coverage_roi', ee.Number(cloud_area).multiply(100))

def apply_cloud_mask_sentinel(image):
    scl = image.select('SCL')
    valid_pixels = scl.eq(4).Or(scl.eq(5)).Or(scl.eq(6)).Or(scl.eq(1))
    return image.updateMask(valid_pixels)

# Funções de mascaramento e cobertura de nuvens para Landsat
def apply_landsat_cloud_mask(image):
    qa = image.select('QA_PIXEL')
    cloud_shadow_bit = 1 << 3
    cloud_bit = 1 << 5
    mask = qa.bitwiseAnd(cloud_shadow_bit).eq(0).And(qa.bitwiseAnd(cloud_bit).eq(0))
    return image.updateMask(mask)

def get_landsat_cloud_coverage(image, roi):
    qa = image.select('QA_PIXEL')
    cloud_bit = 1 << 5
    cloud_mask = qa.bitwiseAnd(cloud_bit).neq(0)
    cloud_area = cloud_mask.reduceRegion(
        reducer=ee.Reducer.mean(),
        geometry=roi,
        scale=30,
        maxPixels=1e6
    ).get('QA_PIXEL')
    return image.set('cloud_coverage_roi', ee.Number(cloud_area).multiply(100))

# Função para verificar pixels válidos
def has_valid_pixels(image, roi, scale):
    """Verifica se a imagem contém pixels válidos após mascaramento."""
    pixel_count = image.reduceRegion(
        reducer=ee.Reducer.count(),
        geometry=roi,
        scale=scale,
        maxPixels=1e6
    ).get(image.bandNames().get(0))
    return ee.Number(pixel_count).gt(0)

# Função para expandir o intervalo de datas
def expand_date_range(start_date, end_date, roi, max_days=90, collection_type='sentinel'):
    collection = None
    if collection_type == 'sentinel':
        collection = (ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED")
                      .filterBounds(roi)
                      .filterDate(start_date, end_date)
                      .map(lambda img: get_cloud_coverage_sentinel(img, roi))
                      .filter(ee.Filter.lt('cloud_coverage_roi', 20))
                      .map(apply_cloud_mask_sentinel))
    elif collection_type == 'landsat':
        collection = (ee.ImageCollection('LANDSAT/LC09/C02/T1_L2')
                      .filterBounds(roi)
                      .filterDate(start_date, end_date)
                      .map(lambda img: get_landsat_cloud_coverage(img, roi))
                      .filter(ee.Filter.lt('cloud_coverage_roi', 20))
                      .map(apply_landsat_cloud_mask))
    elif collection_type == 'chirps':
        collection = (ee.ImageCollection('UCSB-CHG/CHIRPS/DAILY')
                      .filterBounds(roi)
                      .filterDate(start_date, end_date)
                      .select('precipitation'))
    elif collection_type == 'era5_temp':
        collection = (ee.ImageCollection('ECMWF/ERA5_LAND/HOURLY')
                      .filterBounds(roi)
                      .filterDate(start_date, end_date)
                      .select('temperature_2m'))

    return collection

# Função para extrair períodos de datas do request
def extract_date_periods(data):
    """Extrai períodos de datas do JSON da requisição."""
    periods = {}
    
    if 'date_periods' in data and isinstance(data['date_periods'], list):
        for i, period in enumerate(data['date_periods'], 1):
            if isinstance(period, list) and len(period) == 2:
                periods[f'period_{i}'] = {
                    'start_date': period[0],
                    'end_date': period[1]
                }
    else: # Fallback para formato antigo se necessário
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
        if not periods and 'start_date' in data and 'end_date' in data:
            periods['period_1'] = {
                'start_date': data['start_date'],
                'end_date': data['end_date']
            }
    
    return periods if periods else {'period_1': {'start_date': '2024-01-01', 'end_date': '2024-01-28'}}


# >>> INÍCIO DAS FUNÇÕES LÓGICAS (NDVI) <<<
def calculate_ndvi_logic(data):
    try:
        roi = ee.Geometry.Polygon(data['roi']['coordinates'])
        periods = extract_date_periods(data)
        results = {}

        for period_name, dates in periods.items():
            start_date = dates['start_date']
            end_date = dates['end_date']

            collection = expand_date_range(start_date, end_date, roi, collection_type='sentinel')
            best_image = collection.sort('cloud_coverage_roi').first()
            satellite = 'sentinel'
            scale = 10
            
            if not best_image: # Checa se a coleção não está vazia
                 results[period_name] = {'error': 'Nenhuma imagem Sentinel encontrada, tentando Landsat.', 'satellite': 'none'}
            else:
                ndvi = best_image.normalizedDifference(['B8', 'B4']).rename('NDVI').clip(roi)
                if not has_valid_pixels(ndvi, roi, scale).getInfo():
                    best_image = None # Força a checagem do Landsat

            if not best_image:
                collection = expand_date_range(start_date, end_date, roi, collection_type='landsat')
                best_image = collection.sort('cloud_coverage_roi').first()
                satellite = 'landsat'
                scale = 30
                if not best_image:
                    results[period_name] = {'error': 'Nenhuma imagem com pixels válidos na ROI', 'satellite': 'none'}
                    continue
                ndvi = best_image.normalizedDifference(['SR_B5', 'SR_B4']).rename('NDVI').clip(roi)
                if not has_valid_pixels(ndvi, roi, scale).getInfo():
                    results[period_name] = {'error': 'Nenhuma imagem com pixels válidos na ROI', 'satellite': 'none'}
                    continue

            stats = ndvi.reduceRegion(
                reducer=ee.Reducer.mean().combine(reducer2=ee.Reducer.minMax(), sharedInputs=True),
                geometry=roi, scale=scale, maxPixels=1e6
            ).getInfo()

            results[period_name] = {
                'ndvi_mean': stats.get('NDVI_mean'), 'ndvi_min': stats.get('NDVI_min'),
                'ndvi_max': stats.get('NDVI_max'), 'satellite': satellite
            }
        return results
    except Exception as e:
        return {'error': str(e)}

def get_ndvi_tiles_logic(data):
    try:
        roi = ee.Geometry.Polygon(data['roi']['coordinates'])
        periods = extract_date_periods(data)
        vis_params = data.get('vis_params', {'min': 0, 'max': 0.8, 'palette': ['red', 'yellow', 'green']})
        results = {}

        for period_name, dates in periods.items():
            start_date = dates['start_date']
            end_date = dates['end_date']

            collection = expand_date_range(start_date, end_date, roi, collection_type='sentinel')
            best_image = collection.sort('cloud_coverage_roi').first()
            satellite = 'sentinel'
            scale = 10

            if not best_image:
                best_image = None
            else:
                ndvi = best_image.normalizedDifference(['B8', 'B4']).rename('NDVI').clip(roi)
                if not has_valid_pixels(ndvi, roi, scale).getInfo():
                     best_image = None

            if not best_image:
                collection = expand_date_range(start_date, end_date, roi, collection_type='landsat')
                best_image = collection.sort('cloud_coverage_roi').first()
                satellite = 'landsat'
                scale = 30
                if not best_image:
                    results[period_name] = {'error': 'Nenhuma imagem com pixels válidos na ROI', 'satellite': 'none'}
                    continue
                ndvi = best_image.normalizedDifference(['SR_B5', 'SR_B4']).rename('NDVI').clip(roi)
                if not has_valid_pixels(ndvi, roi, scale).getInfo():
                    results[period_name] = {'error': 'Nenhuma imagem com pixels válidos na ROI', 'satellite': 'none'}
                    continue

            map_id_dict = ndvi.getMapId(vis_params)
            results[period_name] = {'tile_url': map_id_dict['tile_fetcher'].url_format, 'satellite': satellite}
        return results
    except Exception as e:
        return {'error': str(e)}

def get_image_tile_logic(data):
    # Esta função permanece a mesma, pois ainda é usada pelo NDVI Composite
    try:
        roi = ee.Geometry.Polygon(data['roi']['coordinates'])
        periods = extract_date_periods(data)
        results = {}
        for period_name, dates in periods.items():
            start_date = dates['start_date']
            end_date = dates['end_date']
            collection = expand_date_range(start_date, end_date, roi, collection_type='sentinel')
            best_image = collection.sort('cloud_coverage_roi').first()
            satellite = 'sentinel'
            scale = 10
            bands = ['B4', 'B3', 'B2']
            if not best_image or not has_valid_pixels(best_image.select(bands), roi, scale).getInfo():
                collection = expand_date_range(start_date, end_date, roi, collection_type='landsat')
                best_image = collection.sort('cloud_coverage_roi').first()
                satellite = 'landsat'
                scale = 30
                bands = ['SR_B4', 'SR_B3', 'SR_B2']
                if not best_image or not has_valid_pixels(best_image.select(bands), roi, scale).getInfo():
                    results[period_name] = {'error': 'Nenhuma imagem com pixels válidos na ROI', 'satellite': 'none'}
                    continue
            best_image = best_image.clip(roi)
            stats = best_image.select(bands).reduceRegion(reducer=ee.Reducer.percentile([15, 85]), geometry=roi, scale=scale, maxPixels=1e6).getInfo()
            vis_params = {'bands': bands, 'min': [stats.get(f'{b}_p15', 300) for b in bands], 'max': [stats.get(f'{b}_p85', 1000) for b in bands], 'gamma': 1.3}
            map_id_dict = best_image.getMapId(vis_params)
            results[period_name] = {'tile_url': map_id_dict['tile_fetcher'].url_format, 'satellite': satellite}
        return results
    except Exception as e:
        return {'error': str(e)}

# >>> INÍCIO DAS FUNÇÕES LÓGICAS CLIMÁTICAS OTIMIZADAS E CORRIGIDAS <<<

def calculate_chirps_logic_optimized(data, point):
    """Calcula estatísticas de precipitação para um ponto - VERSÃO OTIMIZADA E CORRIGIDA."""
    try:
        periods = extract_date_periods(data)
        results = {}
        scale = 5566  # Resolução nativa do CHIRPS

        for period_name, dates in periods.items():
            start_date = dates['start_date']
            end_date = dates['end_date']
            
            # Criar coleção diretamente sem cache problemático
            collection = expand_date_range(start_date, end_date, point, collection_type='chirps')

            # Calcular estatísticas em uma única operação
            precip_sum = collection.sum()
            precip_mean = collection.mean()
            
            # Combinar em uma única imagem para uma única chamada getInfo()
            combined_stats = ee.Image.cat([precip_sum, precip_mean]).rename(['precip_sum', 'precip_mean'])
            
            # Uma única chamada getInfo() em vez de duas
            stats = combined_stats.reduceRegion(
                reducer=ee.Reducer.first(), 
                geometry=point, 
                scale=scale,
                maxPixels=1e6
            ).getInfo()
            
            # Verificar se os valores existem antes de acessar
            precip_sum_val = stats.get('precip_sum')
            precip_mean_val = stats.get('precip_mean')
            
            results[period_name] = {
                'precipitation_sum': precip_sum_val,
                'precipitation_daily_mean': precip_mean_val,
                'source': 'precipitation'
            }
        return results
    except Exception as e:
        return {'error': str(e)}

def calculate_era5_temp_logic_optimized(data, point):
    """Calcula estatísticas de temperatura (mín, máx, média) para um ponto - VERSÃO OTIMIZADA E CORRIGIDA."""
    try:
        periods = extract_date_periods(data)
        results = {}
        scale = 11132  # Resolução nativa do ERA5-Land

        for period_name, dates in periods.items():
            start_date = dates['start_date']
            end_date = dates['end_date']
            
            # Criar coleção diretamente sem cache problemático
            collection = expand_date_range(start_date, end_date, point, collection_type='era5_temp')

            # Calcular min, max e mean em uma única operação
            temp_min_k = collection.min()
            temp_max_k = collection.max()
            temp_mean_k = collection.mean()
            
            # Combinar em uma única imagem para uma única chamada getInfo()
            stats_image_k = ee.Image.cat([temp_min_k, temp_mean_k, temp_max_k]).rename(['temp_min_k', 'temp_mean_k', 'temp_max_k'])
            
            # Uma única chamada getInfo() em vez de múltiplas
            temp_stats_k = stats_image_k.reduceRegion(
                reducer=ee.Reducer.first(), 
                geometry=point, 
                scale=scale,
                maxPixels=1e6
            ).getInfo()

            # Verificar se os valores existem antes de converter
            temp_min_val = temp_stats_k.get('temp_min_k')
            temp_mean_val = temp_stats_k.get('temp_mean_k')
            temp_max_val = temp_stats_k.get('temp_max_k')
            
            # Converter de Kelvin para Celsius apenas se os valores existirem
            results[period_name] = {
                'temperature_min_celsius': temp_min_val - 273.15 if temp_min_val is not None else None,
                'temperature_mean_celsius': temp_mean_val - 273.15 if temp_mean_val is not None else None,
                'temperature_max_celsius': temp_max_val - 273.15 if temp_max_val is not None else None,
                'source': 'temperature'
            }
        return results
    except Exception as e:
        return {'error': str(e)}

# Função genérica para executar tarefas em paralelo e unificar resultados
def run_composite_tasks(data, tasks_to_run, point=None):
    unified_results = {}
    with ThreadPoolExecutor(max_workers=len(tasks_to_run)) as executor:
        if point:
            future_to_task = {executor.submit(task[0], data, point): task[1] for task in tasks_to_run}
        else:
            future_to_task = {executor.submit(task[0], data): task[1] for task in tasks_to_run}
        
        for future in as_completed(future_to_task):
            task_name = future_to_task[future]
            try:
                unified_results[task_name] = future.result()
            except Exception as e:
                unified_results[task_name] = {'error': str(e)}
    return unified_results


# >>> ENDPOINTS DA API <<<

@app.route('/health', methods=['GET'])
def health_check():
    """Endpoint para verificar saúde da aplicação e projeto GEE."""
    try:
        project_info = get_project_info()
        return jsonify({
            'status': 'healthy',
            'gee_project': project_info,
            'timestamp': time.time()
        })
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': time.time()
        }), 500

@app.route('/ndvi_composite', methods=['POST'])
def ndvi_composite():
    try:
        initialize_gee()
        data = request.json
        if not data or 'roi' not in data or 'coordinates' not in data['roi']:
            return jsonify({'error': 'GeoJSON de ROI (polígono) inválido'}), 400
        
        tasks = [
            (calculate_ndvi_logic, 'ndvi'),
            (get_ndvi_tiles_logic, 'ndvi_tiles'),
#            (get_image_tile_logic, 'image_tiles')
        ]
        results = run_composite_tasks(data, tasks)
        
        # Adicionar informações do projeto na resposta
        results['project_info'] = get_project_info()
        
        return jsonify(results)
    except Exception as e:
        return jsonify({'error': str(e), 'project_info': get_project_info()}), 500

@app.route('/climate_stats', methods=['POST'])
def climate_stats():
    start_time = time.time()
    try:
        initialize_gee()
        data = request.json
        if not data or 'point' not in data or 'coordinates' not in data['point']:
            return jsonify({'error': 'GeoJSON de ponto inválido'}), 400
        
        point = ee.Geometry.Point(data['point']['coordinates'])
        
        tasks = [
            (calculate_chirps_logic_optimized, 'precipitation'),
            (calculate_era5_temp_logic_optimized, 'temperature')
        ]
        results = run_composite_tasks(data, tasks, point)
        
        # Adicionar tempo de processamento e informações do projeto
        processing_time = time.time() - start_time
        results['processing_time_seconds'] = round(processing_time, 2)
        results['project_info'] = get_project_info()
        
        return jsonify(results)
    except Exception as e:
        processing_time = time.time() - start_time
        return jsonify({
            'error': str(e), 
            'processing_time_seconds': round(processing_time, 2),
            'project_info': get_project_info()
        }), 500

if __name__ == '__main__':
    # Inicializar GEE na inicialização da aplicação
    try:
        initialize_gee()
        print("🚀 Aplicação Flask iniciada com sucesso!")
    except Exception as e:
        print(f"⚠️ Aviso: Erro na inicialização do GEE: {e}")
    
    # Executar aplicação Flask
    app.run(host='0.0.0.0', port=5000, debug=True)