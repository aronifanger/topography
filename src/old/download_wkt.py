from shapely.wkt import loads
from utils import remove_srid
import requests

# Function definitions
def download_polygon_wkt(osmid):
    """
    Download polygon data from the OpenStreetMap service.
    
    Args:
        osmid (int): The OpenStreetMap ID for the desired polygon.
    
    Returns:
        str: WKT representation of the polygon or an error message.
    """
    base_url = 'https://polygons.openstreetmap.fr'
    response = requests.get(f"{base_url}/get_wkt.py", params={'id': osmid})
    
    if response.ok:
        return response.text
    else:
        return f"Error: Unable to download polygon for OSM ID {osmid}. HTTP Status: {response.status_code}"


if __name__ == '__main__':

    # Download dos dados de São Paulo
    wkt_path = 'data/saopaulo_city_poly.wkt'
    osmid = 298285

    download_polygon_wkt(osmid)