import re
import pandas as pd
from sklearn.neighbors import BallTree
import numpy as np
from pathlib import Path

BASE_PATH = Path("data/elevation")

def get_file_path(lat, lon):

    lon_str = str(int(abs(lon)))

    int_lat = 10 * lat
    round_lat = int_lat - (int_lat % 15)
    lat_str = str(int(abs(round_lat)))

    if lat_str.endswith("0"):
        lat_str = lat_str[:-1] + "_"
    
    file_name = f"{lon_str}_{lat_str}cor_rec.txt"
    
    # Exceptions
    exception_map = {"24_465cor_rec.txt": "23_465cor_rec.txt",
                     "25_48_cor_rec.txt": "24_48_cor_rec.txt",}
    file_name = exception_map.get(file_name, file_name)

    file_path = BASE_PATH / file_name

    if not file_path.exists():
        raise ValueError(f"Arquivo {file_name} não encontrado.")
    
    
    return file_path

class GeoElevationEstimator:
    def __init__(self):
        self.lat_min = 0
        self.lat_max = 0
        self.lon_min = 0
        self.lon_max = 0
        self.tree = None  # Será inicializado após carregar e filtrar os dados
        self.elevations = None  # Também será inicializado apropriadamente
        self.k = 1  # Número de vizinhos para o KNN

    def load(self, lat, lon):

        print(f"Lat, Lon: {lat}, {lon}")
        filepath = get_file_path(lat, lon)
        print(f"Carregando arquivo {filepath}")

        # Carrega os dados do arquivo CSV
        df = pd.read_csv(filepath, sep="\s+", names=["lat", "lon", "elevation"])

        self.lat_min, self.lat_max = df['lat'].min(), df['lat'].max()
        self.lon_min, self.lon_max = df['lon'].min(), df['lon'].max()
                         
        # Preparar os dados para o KNN
        coords = df[['lat', 'lon']].values
        self.elevations = df['elevation'].values
        
        # Construir a BallTree
        self.tree = BallTree(np.deg2rad(coords), metric='haversine')

    @staticmethod
    def _weighted_elevation(neighbors, distances):
        distances = np.maximum(distances, 1e-7)  # Evitar divisão por zero
        weights = 1 / distances
        return np.average(neighbors, weights=weights)

    def estimate_elevation(self, lat, lon):
        if lat > self.lat_max or lat < self.lat_min or lon > self.lon_max or lon < self.lon_min:
            self.load(lat, lon)
            
        dist, indices = self.tree.query(np.deg2rad([[lat, lon]]), k=self.k)
        neighbor_elevations = self.elevations[indices[0]]
        return self._weighted_elevation(neighbor_elevations, dist[0])

if __name__ == '__main__':
    # Uso da classe GeoElevationEstimator
    geo_estimator = GeoElevationEstimator()

    # Estimar a elevação para uma nova coordenada
    new_lat, new_lon = -48.0350, -19.0150
    estimated_elev = geo_estimator.estimate_elevation(new_lat, new_lon)
    print(f'Estimated Elevation: {estimated_elev}')


    # file = get_file_path(-55.4958,     -31.3091)
    # df = pd.read_csv(file, sep="\s+", names=["lat", "lon", "elevation"])
    # lat_min, lat_max = df['lat'].min(), df['lat'].max()
    # lon_min, lon_max = df['lon'].min(), df['lon'].max()
    # print(df.head(5))