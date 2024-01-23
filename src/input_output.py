from pathlib import Path
from shapely.geometry import Polygon, MultiPolygon, mapping, shape
import json

def save_wkt(polygon_wkt, path):
    """
    Save the polygon WKT string to a file.
    
    Args:
        polygon_wkt (str): The WKT representation of the polygon.
        path (str): The file path where to save the WKT.
    """
    with open(path, 'w') as f:
        f.write(polygon_wkt)

def load_wkt(path):
    """
    Read polygon WKT data from a file.
    
    Args:
        path (str): The file path containing the polygon WKT.
    
    Returns:
        str: The WKT data.
    """
    with open(path, 'r') as f:
        return f.read()
    
def save_multipolygon(multipolygon, file_path):
    if not isinstance(multipolygon, MultiPolygon):
        raise ValueError('The input must be a shapely.geometry.MultiPolygon')
    
    # Converta cada Polygon do MultiPolygon para um formato serializável (dicionário)
    triangle_dicts = [mapping(polygon) for polygon in multipolygon.geoms]
    
    # Salve os triângulos em um arquivo usando JSON
    with open(file_path, 'w') as file:
        json.dump(triangle_dicts, file)

def load_multipolygon(file_path):
    # Carrega os triângulos de um arquivo JSON e transforma de volta em objetos Polygon
    with open(file_path, 'r') as file:
        triangle_dicts = json.load(file)
    
    # Cria os objetos Polygon a partir dos dados
    triangles = [shape(triangle_dict) for triangle_dict in triangle_dicts]
    
    # Cria um MultiPolygon com os triângulos carregados
    multipolygon = MultiPolygon(triangles)
    return multipolygon

def save_polygon(polygon, file_path):
    if not isinstance(polygon, Polygon):
        raise ValueError('The input must be a shapely.geometry.Polygon')
    
    # Converta o Polygon para um formato serializável (dicionário)
    polygon_dict = mapping(polygon)
    
    # Salve o Polygon em um arquivo usando JSON
    with open(file_path, 'w') as file:
        json.dump(polygon_dict, file)

def load_polygon(file_path):
    # Carrega o Polygon de um arquivo JSON e o transforma de volta em um objeto Polygon
    with open(file_path, 'r') as file:
        data = json.load(file)
        
    # Verifique se o dado carregado é um dicionário e não uma lista
    if not isinstance(data, dict):
        raise ValueError('The JSON file should contain a dictionary representing a Polygon, not a list.')
    
    # Cria o objeto Polygon a partir dos dados
    polygon = shape(data)
    return polygon


# Função para carregar cache de altitudes de um arquivo
def load_cache(cache_file):
    """
    Load altitude cache from a file.
    
    Args:
        cache_file (str): The file path to the cache file.

    Returns:
        dict: A dictionary containing cached altitudes.
    """
    if Path(cache_file).is_file():
        with open(cache_file, 'r') as file:
            cache = json.load(file)
    else:
        cache = {}
    return cache

# Função para salvar o cache de altitudes em um arquivo
def save_cache(cache, cache_file):
    """
    Save altitude cache to a file.
    
    Args:
        cache (dict): A dictionary containing altitudes to cache.
        cache_file (str): The file path to save the cache file.
    """
    with open(cache_file, 'w') as file:
        json.dump(cache, file, indent=4)