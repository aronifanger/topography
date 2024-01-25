from src.input_output import load_wkt, save_polygon
from scipy.spatial import Delaunay
from shapely.geometry import Polygon, MultiPolygon, Point
from shapely.wkt import loads
from stl import mesh
from src.utils import remove_srid
import numpy as np

def wkt_to_polygon(wkt_str):
    # Primeiro, carregamos a string WKT usando a função loads da Shapely
    geometry = loads(remove_srid(wkt_str))

    # Verificamos se a geometria é do tipo Polygon ou MultiPolygon
    if isinstance(geometry, (Polygon, MultiPolygon)):
        # Se for um MultiPolygon, podemos querer trabalhar com o primeiro polígono
        if isinstance(geometry, MultiPolygon):
            # Atenção: isso pega apenas o primeiro polígono de um MultiPolygon!
            return geometry.geoms[0]
        else:
            # Se for um simples Polygon, simplesmente retornamos a geometria
            return geometry
    else:
        raise ValueError("A string WKT fornecida não representa um Polygon ou MultiPolygon.")
    

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


def normalize_multipolygon(multipolygon, scale=(1, 1, 1)):
    # Calcular os mínimos de todas as coordenadas para a translação
    all_coords = [point for polygon in multipolygon.geoms for point in polygon.exterior.coords]
    min_x = min(x for x, y, z in all_coords)
    min_y = min(y for x, y, z in all_coords)
    min_z = min(z for x, y, z in all_coords)
    
    def normalize_point(x, y, z):
        # Reduzindo a escala do eixo z em 1000x
        new_z = z / 1000.0
        # Aplicando translação para que os pontos mínimos fiquem em 0,0,0
        new_x = x - min_x
        new_y = y - min_y
        new_z = new_z - min_z
        # Aplicando a escala adicional fornecida
        new_x *= scale[0]
        new_y *= scale[1]
        new_z *= scale[2]
        return (new_x, new_y, new_z)
    
    # Criar e retornar um novo MultiPolygon normalizado
    normalized_polygons = []
    for polygon in multipolygon.geoms:
        new_exterior = [normalize_point(x, y, z) for x, y, z in polygon.exterior.coords]
        # Polygon espera que o primeiro e o último ponto sejam iguais; ao criar o new_polygon, eles serão verificados
        new_polygon = Polygon(new_exterior)
        normalized_polygons.append(new_polygon)
    
    # Unimos todos os polígonos normalizados em um MultiPolygon
    return MultiPolygon(normalized_polygons)


from shapely.geometry import MultiPolygon, Polygon

def normalize_multipolygon_3d(multipolygon):
    # Calcular os limites dos polígonos
    min_x = min(coord[0] for p in multipolygon.geoms for coord in p.exterior.coords)
    min_y = min(coord[1] for p in multipolygon.geoms for coord in p.exterior.coords)
    min_z = min(coord[2] for p in multipolygon.geoms for coord in p.exterior.coords)

    # O fator de escala para o eixo z é fixo: 1/1000
    scale_z = 1 / 1000

    # Normalizar cada polígono
    normalized_polygons = []
    for polygon in multipolygon.geoms:
        # Normalizar as coordenadas considerando a diminuição do eixo 'z'
        norm_coords = [(
            coord[0] - min_x,  # Translação para a origem no eixo x
            coord[1] - min_y,  # Translação para a origem no eixo y
            (coord[2] * scale_z) - min_z  # Redução da escala no eixo z e translação para a origem
        ) for coord in polygon.exterior.coords]
        
        # Criar um novo polígono com as coordenadas normalizadas
        norm_polygon = Polygon(norm_coords)
        normalized_polygons.append(norm_polygon)
    
    # Criar um novo multipolygon com os polígonos normalizados
    normalized_multipolygon = MultiPolygon(normalized_polygons)
    return normalized_multipolygon


def create_grid_polygon(polygon, step=0.1):

    # Crie a malha de pontos
    x_min, y_min, x_max, y_max = polygon.bounds
    x_points = np.arange(x_min, x_max, step)
    y_points = np.arange(y_min, y_max, step)
    points = np.array([[x, y] for x in x_points for y in y_points if polygon.contains(Point(x, y))])

    # Verifique se há pontos suficientes para triangulação
    if len(points) < 3:
        return MultiPolygon()

    # Realize a triangulação de Delaunay
    tri = Delaunay(points)
    
    # Crie os triângulos com base em Delaunay triangulation
    triangles = []
    for simplex in tri.simplices:
        tri_points = points[simplex]
        triangle = Polygon(tri_points)
        if polygon.contains(triangle):  # Verifique se o triângulo está totalmente dentro do polígono
            triangles.append(triangle)

    # Converta os triângulos em um MultiPolygon
    multipolygon = MultiPolygon(triangles)

    return multipolygon



if __name__ == "__main__":

    # Download dos dados de São Paulo
    wkt_path = 'data/saopaulo_city_poly.wkt'
    png1_path = 'data/saopaulo_city_poly.png'
    png2_path = 'data/saopaulo_city_poly_triangles.png'
    pol_path = 'data/saopaulo_city_poly.json'
    tri_path = 'data/saopaulo_city_poly_triangles.json'
    stl_path = 'data/saopaulo_city_poly.stl'

    polygon_wkt = load_wkt(wkt_path)
    polygon = wkt_to_polygon(polygon_wkt)
    save_polygon(polygon, pol_path)
    # polygon = normalize_polygon(polygon)
    # plot_and_save_geometry(polygon, png1_path)
    # triangles = create_grid_polygon(polygon)
    # # triangles = triangulate_with_area_constraint(polygon, 0.0001)
    # load_multipolygon(triangles, tri_path)
    # plot_and_save_geometry(triangles, png2_path, dpi=1000)
