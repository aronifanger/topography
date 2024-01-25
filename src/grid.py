from shapely.geometry import MultiPolygon, Polygon
from src.visualization import plot_and_save_geometry
from src.input_output import save_multipolygon

def generate_triangle_mesh(x_min=0, y_min=0, x_max=20, y_max=20, triangle_base=1):
    # altura de um triângulo equilátero
    triangle_height = float(triangle_base) * (3. ** (1./3.)) / 2.
    # Verificações básicas para garantir que a base e altura são adequadas
    if triangle_height <= 0 or triangle_base <= 0:
        raise ValueError("Base e altura devem ser maiores que zero.")
    
    if x_max - x_min <= 0 or y_max - y_min <= 0:
        raise ValueError("Dimensões do espaço devem ser maiores que zero.")
    
    # Base horizontal do triângulo
    half_base = triangle_base / 2
    mesh = []
    
    # Cria os triângulos em linhas alternadas
    y = y_min

    alternate_row = False  # Alternar a orientação do triângulo
    while y + triangle_height <= y_max:
        x = x_min
        alternate_col = alternate_row  # Alternar a orientação do triângulo

        if alternate_col:
            # Triângulo apontando para cima
            mesh.append(Polygon([(x, y + triangle_height), (x, y), (x + half_base, y + triangle_height)]))
        else:
            # Triângulo apontando para baixo
            mesh.append(Polygon([(x, y), (x, y + triangle_height), (x + half_base, y)]))
        
        
        while x + half_base <= x_max:
            if alternate_col:
                # Triângulo apontando para cima
                mesh.append(Polygon([(x, y), (x + half_base, y + triangle_height), (x + triangle_base, y)]))
            else:
                # Triângulo apontando para baixo
                mesh.append(Polygon([(x, y + triangle_height), (x + half_base, y), (x + triangle_base, y + triangle_height)]))

            # Move para o próximo ponto no eixo x
            x += half_base
            alternate_col = not alternate_col
        
        # Último triângulo
        if alternate_col:
            # Triângulo apontando para cima
            mesh.append(Polygon([(x, y), (x + half_base, y + triangle_height), (x + half_base, y)]))
        else:
            # Triângulo apontando para baixo
            mesh.append(Polygon([(x, y + triangle_height), (x + half_base, y), (x + half_base, y + triangle_height)]))

            
        # Move para o próximo ponto no eixo y
        y += triangle_height

        alternate_row = not alternate_row
    # Combina todos os polígonos em um MultiPolygon
    mesh_shape = MultiPolygon(mesh)
    return mesh_shape

if __name__ == "__main__":
    # Exemplo de uso
    x_min, y_min = 0, 0
    x_max, y_max = 20, 20
    triangle_base = 0.5
    str_param = str(triangle_base).replace(".", "")
    
    mesh_shape = generate_triangle_mesh(x_min, y_min, x_max, y_max, triangle_base)
    plot_and_save_geometry(mesh_shape, f'data/grid_{str_param}.png')
    save_multipolygon(mesh_shape, f'data/grid_{str_param}.json')