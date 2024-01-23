from shapely.geometry import Polygon, MultiPolygon, shape
from stl import mesh
import json
import numpy as np





def multipolygon_to_stl(multipolygon, filename):
    """
    Transforma um objeto MultiPolygon do Shapely em um arquivo STL.

    :param multipolygon: Um objeto Shapely MultiPolygon contendo triângulos.
    :param filename: Nome do arquivo STL de saída.
    """
    assert isinstance(multipolygon, MultiPolygon), "O objeto deve ser um MultiPolygon do Shapely."

    # Criar uma lista para armazenar os vértices para o Mesh
    vertices = []

    for polygon in multipolygon.geoms:  # Iterar através dos Polygons dentro do MultiPolygon
        if isinstance(polygon, Polygon):
            exterior_coords = polygon.exterior.coords
            for i in range(1, len(exterior_coords) - 2):
                # Cada triângulo é formado pelo primeiro ponto do exterior e dois pontos consecutivos
                tri = [exterior_coords[0], exterior_coords[i], exterior_coords[i+1]]
                vertices.extend(tri)

    # Criando o modelo STL
    stl_mesh = mesh.Mesh(np.zeros(len(vertices) // 3, dtype=mesh.Mesh.dtype))

    for i in range(len(vertices) // 3):
        stl_mesh.vectors[i] = np.array(vertices[3*i:3*i+3])

    # Escrevendo o arquivo STL
    stl_mesh.save(filename)

def normalize_multipolygon(multipolygon, x_y_scale=(19, 19), z_scale=(2, 0)):
    # Calcular os mínimos e máximos de todas as coordenadas
    all_coords = [point for polygon in multipolygon.geoms for point in polygon.exterior.coords]
    min_x = min(x for x, y, z in all_coords)
    max_x = max(x for x, y, z in all_coords)
    min_y = min(y for x, y, z in all_coords)
    max_y = max(y for x, y, z in all_coords)
    min_z = min(z for x, y, z in all_coords)
    max_z = max(z for x, y, z in all_coords)
    
    # Calcular o intervalo de X e Y mantendo a proporção
    coord_range = max(max_x - min_x, max_y - min_y)
    x_y_scale_factor = x_y_scale[0] / coord_range
    z_scale_factor = z_scale[0] / (max_z - min_z)
    
    def normalize_point(x, y, z):
        # Normalizar o ponto mantendo as proporções para X e Y
        new_x = (x - min_x) * x_y_scale_factor + 1  # +1 para margem de 1cm
        # Certificar de reverter o Y para manter a orientação original do polígono
        new_y = (y - min_y) * x_y_scale_factor + 1  # +1 para margem de 1cm
        new_z = (z - min_z) * z_scale_factor + z_scale[1]  # +0 porque estamos começando de 0 para a altura
        return (new_x, new_y, new_z)
    
    # Criar e retornar um novo MultiPolygon normalizado
    normalized_polygons = []
    for polygon in multipolygon.geoms:
        new_exterior = [normalize_point(x, y, z) for x, y, z in polygon.exterior.coords]
        new_polygon = Polygon(new_exterior[:-1])  # Excluir último ponto pois é uma repetição do primeiro
        normalized_polygons.append(new_polygon)
    
    # Unimos todos os polígonos normalizados em um MultiPolygon
    return MultiPolygon(normalized_polygons)

if __name__ == "__main__":

    p3d_path = 'data/saopaulo_city_surface.json'
    stl_path = 'data/saopaulo_city_surface.stl'

    polygon = load_multipolygon(p3d_path)
    norm_poly = normalize_multipolygon(polygon)
    # Chama a função para converter para um arquivo STL
    multipolygon_to_stl(norm_poly, filename=stl_path)