from pathlib import Path
from shapely.geometry import Polygon, MultiPolygon, mapping, shape
from tqdm import tqdm
from typing import Union
import json
import requests


# Global definition for the altitude cache file
CACHE_FILE = "data/altitude_cache.json"

def save_triangles_to_file(multipolygon, file_path):
    if not isinstance(multipolygon, MultiPolygon):
        raise ValueError('The input must be a shapely.geometry.MultiPolygon')
    
    # Converta cada Polygon do MultiPolygon para um formato serializável (dicionário)
    triangle_dicts = [mapping(polygon) for polygon in multipolygon.geoms]
    
    # Salve os triângulos em um arquivo usando JSON
    with open(file_path, 'w') as file:
        json.dump(triangle_dicts, file)

def load_triangles_from_file(file_path):
    # Carrega os triângulos de um arquivo JSON e transforma de volta em objetos Polygon
    with open(file_path, 'r') as file:
        triangle_dicts = json.load(file)
    
    # Cria os objetos Polygon a partir dos dados
    triangles = [shape(triangle_dict) for triangle_dict in triangle_dicts]
    
    # Cria um MultiPolygon com os triângulos carregados
    multipolygon = MultiPolygon(triangles)
    return multipolygon

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

# Função para obter altitudes de uma lista de coordenadas
def get_altitudes(points, api_key, cache_file=CACHE_FILE):
    """
    Retrieve altitudes for a list of coordinates from Google Elevation API.
    
    Args:
        points (list): A list of point tuples in (latitude, longitude) format.
        api_key (str): Google Elevation API key.
        cache_file (str, optional): Path to a cache file.

    Returns:
        list: List of altitudes corresponding to the input points.
    """
    cache = load_cache(cache_file)
    
    altitudes = {}
    base_url = "https://maps.googleapis.com/maps/api/elevation/json"
    
    for point in points:
        location = f"{point[0]},{point[1]}"
        
        # Check if altitude is already in cache
        if location in cache:
            altitudes[location] = cache[location]["elevation"]
        else:
            # Query the API for elevation if not in cache
            params = {'locations': location, 'key': api_key}
            response = requests.get(base_url, params=params)
            
            if response.status_code == 200:
                result = response.json()
                if result['status'] == 'OK' and result['results']:
                    elevation = result['results'][0]['elevation']
                    altitudes[location] = elevation
                    # Update cache with new altitude
                    cache[location] = result['results'][0]
                else:
                    altitudes[location] = None  # Handle no result response
            else:
                altitudes[location] = None  # Handle response error

            # Save cache progress to cache file
            save_cache(cache, cache_file)
    
    return [altitudes[location] for location in altitudes]


def add_altitude_to_coords(coords, api_key, cache_file=CACHE_FILE):
    """
    Add altitude information to a list of coordinates.

    Args:
        coords (list): A list of coordinate tuples (latitude, longitude).
        api_key (str): The API key for the elevation service.
        cache_file (str): The path to the cache file for storing elevation data.

    Returns:
        list: A list of coordinates with altitude information (latitude, longitude, altitude).
    """
    altitudes = get_altitudes(coords, api_key, cache_file=cache_file)
    final_coords = []
    for (lat, lon), alt in zip(coords, altitudes):
        final_coords.append((lat, lon, alt))
    return final_coords

def add_altitude_to_geometry(geometry: Union[Polygon, MultiPolygon], api_key: str, cache_file: str = 'elevation_cache.json') -> Union[Polygon, MultiPolygon]:
    """
    Adiciona informações de altitude a um Polygon ou MultiPolygon 2D usando uma API de serviço de elevação.

    :param geometry: Um objeto Polygon ou MultiPolygon 2D.
    :param api_key: A chave da API para o serviço de elevação.
    :param cache_file: O caminho do arquivo de cache para armazenar dados de elevação.
    :return: Um objeto Polygon ou MultiPolygon com informações de altitude.
    """
    
    def add_altitude_to_coords(coords, api_key, cache_file):
        # A função de adicionar altitude é o corpo que você forneceu na pergunta
        altitudes = get_altitudes(coords, api_key, cache_file=cache_file)
        final_coords = []
        for (lat, lon), alt in zip(coords, altitudes):
            final_coords.append((lat, lon, alt))
        return final_coords
    
    def process_polygon(polygon):
        exterior = add_altitude_to_coords(list(polygon.exterior.coords), api_key, cache_file)
        interiors = [add_altitude_to_coords(list(interior.coords), api_key, cache_file) for interior in polygon.interiors]
        return Polygon(exterior, interiors)
    
    if isinstance(geometry, Polygon):
        return process_polygon(geometry)

    elif isinstance(geometry, MultiPolygon):
        polygons = [process_polygon(polygon) for polygon in tqdm(geometry.geoms)]
        return MultiPolygon(polygons)

    else:
        raise TypeError("Input must be a Polygon or MultiPolygon")
    
if __name__ == "__main__":

    # api_key = "AIzaSyAYDl7JCfzqeOVZQlUpRXMWmt_Ctafx-9Y"
    tri_path = 'data/saopaulo_city_poly_triangles.json'
    p3d_path = 'data/saopaulo_city_poly_surface.json'

    polygon = load_triangles_from_file(tri_path)
    polygon3d = add_altitude_to_geometry(polygon, api_key, CACHE_FILE)
    save_triangles_to_file(polygon3d, p3d_path)