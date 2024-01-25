from src.elevatrion_estimator import GeoElevationEstimator
from src.input_output import load_multipolygon, save_multipolygon, load_polygon
from src.poly_scaler import PolyScaler
from shapely.geometry import Polygon, MultiPolygon, Point
from tqdm import tqdm
from src.visualization import plot_multipolygon3d
import numpy as np



# Função para obter altitudes de uma lista de coordenadas
def get_altitudes(points):
    """
    Retrieve altitudes for a list of coordinates from Model.

    Args:
        points (list): A list of point tuples in (latitude, longitude) format.
        file_path (str): Path to the CSV file containing coordinates and elevations.

    Returns:
        list: List of altitudes corresponding to the input points.
    """    
    # Inicializar e carregar o modelo
    geo_estimator = GeoElevationEstimator()
    
    # Calcular as elevações para cada ponto fornecido
    altitudes = [geo_estimator.estimate_elevation(lat, lon) for lat, lon in tqdm(points, desc="Getting elevation")]
    
    return altitudes

    
def assign_z_coordinate(polygon, multipolygon, include_bottom):
    """
    Transforma um MultiPolygon 2D para 3D seguindo as regras:
    z = 1, se o ponto do multipolygon estiver contido no polygon
    z = 0, caso contrário (somente se include_bottom for True)

    :param polygon: Polygon - um polígono Shapely Polygon.
    :param multipolygon: MultiPolygon - um multipolígono Shapely MultiPolygon.
    :param include_bottom: bool - inclui ou não os pontos externos com z = 0.
    :return: MultiPolygon - um novo multipolígono com coordenadas Z.
    """
    new_polygons = []

    for poly in multipolygon.geoms:
        new_exterior_coords = []
        for x, y in poly.exterior.coords[:-1]:
            if polygon.contains(Point(x, y)) or include_bottom:
                new_exterior_coords.append((x, y, 1 if polygon.contains(Point(x, y)) else 0))

        if len(new_exterior_coords) >= 3:  # Garantindo que temos um polígono válido
            new_exterior_coords.append(new_exterior_coords[0])  # Fechando o anel

            new_interiors = []
            for interior in poly.interiors:
                new_interior_coords = []
                for x, y in interior.coords[:-1]:
                    if polygon.contains(Point(x, y)) or include_bottom:
                        new_interior_coords.append((x, y, 1 if polygon.contains(Point(x, y)) else 0))
                if new_interior_coords:
                    new_interior_coords.append(new_interior_coords[0])  # Fechando o anel
                    new_interiors.append(new_interior_coords)

            new_polygon = Polygon(new_exterior_coords, new_interiors)
            new_polygons.append(new_polygon)

    return MultiPolygon(new_polygons)

def update_z_dimension(multipolygon):
    # Filtra pontos com z=1 e remove duplicatas
    unique_points = set()
    for polygon in multipolygon.geoms:
        for coord in np.asarray(polygon.exterior.coords):
            if coord[2] == 1:
                index = str(int(abs(coord[1]))) + str(int(abs(coord[0]) * 10))
                unique_points.add((coord[0], coord[1], index))

    unique_points = sorted(unique_points, key=lambda x: x[2])
    unique_points = [(lat, lon) for lat, lon, _, in unique_points]

    if unique_points:
        # Obtém altitudes para os pontos filtrados
        altitudes = get_altitudes(list(unique_points))
        
        # Cria um mapeamento ponto para altitude
        altitudes_map = {point: altitude for point, altitude in zip(unique_points, altitudes)}
        
        # Altitude mínima das altitudes obtidas
        min_altitude = min(altitudes)
        max_altitude = max(altitudes)
        range_altitude = max_altitude - min_altitude
        bottom_altitude = min_altitude - (0.1 * range_altitude)
    else:
        min_altitude = 1  # Valor padrão se não houver altitudes

    # Função para atualizar o Z
    def update_z(coords, alt_map, min_alt):
        new_coords = []
        for x, y, z in coords:
            if z == 1:
                new_coords.append((x, y, alt_map.get((x, y), min_alt)))
            else:
                new_coords.append((x, y, bottom_altitude))
        return new_coords

    # Atualiza cada polígono no MultiPolygon
    updated_polygons = []
    for polygon in multipolygon.geoms:
        exterior = update_z(polygon.exterior.coords, altitudes_map, min_altitude)
        interiors = [update_z(interior.coords, altitudes_map, min_altitude) for interior in polygon.interiors]
        updated_polygons.append(Polygon(exterior, interiors))

    # Cria e retorna o MultiPolygon atualizado
    return MultiPolygon(updated_polygons)

if __name__ == "__main__":

    grd_path = 'data/grid/grid_05.json'
    tri_path = 'data/saopaulo_city/poly_05.json'
    p3d_path = 'data/saopaulo_city/flat_surface_05.json'
    f3d_path = 'data/saopaulo_city/flat_surface_05.png'
    s3d_path = 'data/saopaulo_city/surface_05.json'

    polygon = load_polygon(tri_path)
    scaler = PolyScaler()
    scaler.fit(polygon)
    grid = load_multipolygon(grd_path)
    grid = scaler.inverse_transform(grid)
    polygon3d = assign_z_coordinate(polygon, grid, include_bottom=True)
    save_multipolygon(polygon3d, p3d_path)
    plot_multipolygon3d(polygon3d, f3d_path)
    
    polygon3d = update_z_dimension(polygon3d, include_bottom=True)
    save_multipolygon(polygon3d, s3d_path)