from src.main import generate_city_stl_with_base

country_dict = {
    'brasil_country': 59470,
}

states_dict = {
    # 'saupaulo_state': 298204,
    'riodejaneiro_state': 57963,
    'minasgerais_state': 315173,
    'espiritosanto_state': 54882,
    'parana_state': 297640,
    'santacatarina_state': 296584,
    'riograndedosul_state': 242620,
    'matogrossodosul_state': 334051,
    'matogrosso_state': 333597,
    'goias_state': 334443,
}

city_dict = {
    'belohorizonte_city': 368782,
    'saojosedoscampos_city': 298019,
    'saopaulo_city': 298285,
}

regions_dict = {
    'valedoparaiba_region': 2661856,
}

parks_dict = {
    'nacionaldeitatiaia_park': 14406059,
}

custom_map_dict = [
    "serrafina_custom",
]

def process_map(maps, grid_step = 0.1, include_bottom = True):
    for map_name in maps:
        print("Criando o map: " + map_name)
        if type(maps) == dict:
            generate_city_stl_with_base(maps[map_name], map_name, grid_step, include_bottom)
        else:
            generate_city_stl_with_base(0, map_name, grid_step, include_bottom)
        print("Mapa criado com sucesso!\n\n\n\n")


if __name__ == '__main__':
    grid_step = 0.5
    include_bottom = True
    process_map(country_dict, grid_step, include_bottom)
    process_map(states_dict, grid_step, include_bottom)
    process_map(city_dict, grid_step, include_bottom)
    process_map(regions_dict, grid_step, include_bottom)
    process_map(parks_dict, grid_step, include_bottom)
    process_map(custom_map_dict, grid_step, include_bottom)