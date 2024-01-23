from matplotlib import pyplot as plt
from shapely.geometry import Polygon, MultiPolygon

def plot_and_save_geometry(geometry, filename, file_format='png', dpi=300):
    # Verifica se o objeto é do tipo Polygon ou MultiPolygon
    if not isinstance(geometry, (Polygon, MultiPolygon)):
        raise ValueError("O objeto fornecido não é um shapely.geometry.Polygon ou shapely.geometry.MultiPolygon")

    # Inicia um novo plot
    fig, ax = plt.subplots()

    # Se for Polygon, executa o seguinte bloco
    if isinstance(geometry, Polygon):
        # Extrai as coordenadas externas do polígono
        x, y = geometry.exterior.xy

        # Plota o polígono
        ax.fill(x, y, alpha=0.5, fc='blue', ec='black')

    # Se for MultiPolygon, itera por cada Polygon
    elif isinstance(geometry, MultiPolygon):
        for polygon in geometry.geoms:
            # Extrai as coordenadas externas do polígono
            x, y = polygon.exterior.xy

            # Plota o polígono
            ax.fill(x, y, alpha=0.5, fc='blue', ec='black')

            # É possível também plotar os buracos internos, se existirem

    # Define o limite dos eixos para enquadrar a geometria corretamente
    minx, miny, maxx, maxy = geometry.bounds

    ax.set_xlim(minx, maxx)
    ax.set_ylim(miny, maxy)

    # Configura o aspecto dos eixos como 'equal' para evitar distorção
    ax.set_aspect('equal')

    # Remove os eixos para uma visualização mais limpa
    ax.axis('off')

    filename = filename.replace('.json', 'png')

    # Salva o plot em um arquivo
    plt.savefig(filename, format=file_format, bbox_inches='tight', pad_inches=0, dpi=dpi)
    plt.close(fig)  # Fecha a figura para liberar a memória

    print(f"Geometria salva como '{filename}' no formato '{file_format}'")


from shapely.geometry import MultiPolygon
from matplotlib import pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import numpy as np

def plot_multipolygon3d(multipolygon, filename):
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    
    # Para cada polígono no MultiPolygon
    for polygon in multipolygon.geoms:  # Usar o atributo `geoms` aqui
        if not polygon.is_empty:
            # Para cada anel exterior/interior (exterior primeiro, depois os interiores)
            for ring in [polygon.exterior] + list(polygon.interiors):
                x, y = ring.xy
                z = np.zeros_like(x)  # Zeros para representar a altura 0 (no plano XY)
                vertices = [list(zip(x, y, z))]
                ax.add_collection3d(Poly3DCollection(vertices))

    # Definindo limites e ângulos do gráfico
    ax.autoscale()
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')
    
    # Rotação do ponto de vista. (elevação, azimute)
    ax.view_init(30, 45)

    # Personalizar aqui para corresponder à área dos polígonos (opcional)
    # ax.set_xlim([xmin, xmax])
    # ax.set_ylim([ymin, ymax])
    # ax.set_zlim([zmin, zmax])

    # Salvar o plot como um arquivo PNG
    plt.savefig(filename, dpi=300, bbox_inches='tight', pad_inches=0)
    plt.close(fig)