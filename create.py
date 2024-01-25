from src.main import generate_city_stl_with_base

params = [
    # ('belohorizonte_city',        368782, 0.5, True),
    # ('saojosedoscampos_city',     298019, 0.5, True),
    # ('saopaulo_city',             298285, 0.5, True),
    # ('saupaulo_state',            298204, 0.5, True),
    
    # ('belohorizonte_city',        368782, 0.1, True),
    # ('saojosedoscampos_city',     298019, 0.1, True),
    # ('saopaulo_city', 2           298285, 0.1, True),
    # ('saupaulo_state',            298204, 0.1, True),

    # ('belohorizonte_city',        368782, 0.5, False),
    # ('saojosedoscampos_city',     298019, 0.5, False),
    # ('saopaulo_city',             298285, 0.5, False),
    # ('saupaulo_state',            298204, 0.5, False),
    
    # ('belohorizonte_city',        368782, 0.1, False),
    # ('saojosedoscampos_city',     298019, 0.1, False),
    # ('saopaulo_city',             298285, 0.1, False),
    ('saupaulo_state',            298204, 0.1, False),
]
for location_name, osmid, grid_step, include_bottom in params:
    generate_city_stl_with_base(osmid, location_name, grid_step, include_bottom)