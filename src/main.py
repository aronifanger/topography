from src.input_output import save_multipolygon, load_wkt, save_wkt
from src.visualization import plot_and_save_geometry

from src.download import download_polygon_wkt
from src.grid import generate_triangle_mesh
from src.transform import wkt_to_polygon, normalize_multipolygon, multipolygon_to_stl
from src.surface import load_multipolygon, assign_z_coordinate, update_z_dimension

from pathlib import Path
from src.poly_scaler import PolyScaler
import os


def generate_city_stl_with_base(osmid, location_name, grid_step, include_bottom):

    grid_spec = str(grid_step).replace(".", "")
    bottom_spec = "with_bottom" if include_bottom else "without_bottom"
    param_spec = f'{grid_spec}_{bottom_spec}'
    grid_path = f'data/grids/grid_{param_spec}'

    # Downloadin data (donwload_wkt.py)
    location_folder = Path(f'data/maps/{location_name}')
    if not location_folder.exists():
        os.makedirs(location_folder)

    wkt_path = location_folder / f"poly_{param_spec}.wkt"
    if not wkt_path.exists():
        wkt = download_polygon_wkt(osmid)
        save_wkt(wkt, wkt_path)

    # Triangulation (transform.py)
    polygon_wkt = load_wkt(wkt_path)
    polygon = wkt_to_polygon(polygon_wkt)
    
    plot_and_save_geometry(polygon, f'data/maps/{location_name}/poly_{param_spec}.png')

    # Loading Grid (generate_grid.py)
    if not Path(grid_path + '.png').exists():
        grid = generate_triangle_mesh(triangle_base=grid_step)
        plot_and_save_geometry(grid, grid_path + '.png')
        save_multipolygon(grid, grid_path + '.json')
    else:
        grid = load_multipolygon(grid_path + '.json')

    # Surface (surface_From_grid.py)
    scaler = PolyScaler()
    scaler.fit(polygon)
    grid = scaler.inverse_transform(grid)
    polygon3d = assign_z_coordinate(polygon, grid, include_bottom)
    save_multipolygon(polygon3d, f'data/maps/{location_name}/flat_surface_{param_spec}.json')
    polygon3d = update_z_dimension(polygon3d)
    save_multipolygon(polygon3d, f'data/maps/{location_name}/surface_{param_spec}.json')

    # STL generation (stl_generation.py)
    norm_poly = normalize_multipolygon(polygon3d)
    # Chama a função para converter para um arquivo STL
    multipolygon_to_stl(norm_poly, filename=f'data/maps/{location_name}/surface_{param_spec}.stl')


if __name__ == '__main__':
    params = [
        # ('saopaulo_city', 298285, 0.5, True),
        # ('saojosedoscampos_city', 298019, 0.5, True),
        # ('belohorizonte_city', 368782, 0.5, True),
        ('saupaulo_state', 298204, 0.5, True),
        
        # ('saopaulo_city', 298285, 0.1, True),
        # ('saojosedoscampos_city', 298019, 0.1, True),

        # ('saopaulo_city', 298285, 0.5, False),
        
        # ('saopaulo_city', 298285, 0.1, False),
        # ('saupaulo_state', 298204, 0.1, False),
    ]
    for location_name, osmid, grid_step, include_bottom in params:
        generate_city_stl_with_base(osmid, location_name, grid_step, include_bottom)
