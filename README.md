## Localizar o ID da região no site Nominatim

- https://nominatim.openstreetmap.org/ui/details.html?osmtype=R&osmid=298285&class=boundary
- osmid = 298285

## Baixar o polígono  usando o site Open Street Map

- https://polygons.openstreetmap.fr/get_wkt.py?id=298285&params=0




## Baixando dados de altimetria do INPE
- Identificar os quadrantes na imagem (http://www.dsr.inpe.br/topodata/acesso.php)
  - Utilizar a imagem acima para tratar exceções
- Link para download (http://www.dsr.inpe.br/topodata/data/txt/23_435txt.zip)


## Criando um mapa customizado

- Utilize o Google maps para definir o mapa.
  - https://www.google.com/maps/d/edit?mid=1sIOgANrFCwINYfYhMGrMDn7nsdfDCjM
- Crie uma pasta chamada data/maps/<nome_da_regiao>_custom
- Baixe o polígono no formato CSV
- Remova o header e as demais colunas deixando apenas o poígono
- Renomeie para "data/maps/<nome_da_regiao>_custom/boundaries.wkt"
- Execute normalmente passando o nome da região 
