from io import BytesIO
from pathlib import Path
from tqdm import tqdm
import os
import pandas as pd
import requests
import zipfile
import re

BASE_URL = "http://www.dsr.inpe.br/topodata/data/txt/{sheet_id}"
# IDs do estado de São Paulo
ID_LIST = [
    "22_54_txt.zip", "19_525txt.zip", "20_525txt.zip", "21_525txt.zip", "22_525txt.zip", "19_51_txt.zip", "20_51_txt.zip", 
    "21_51_txt.zip", "22_51_txt.zip", "19_495txt.zip", "20_495txt.zip", "21_495txt.zip", "22_495txt.zip", "23_495txt.zip", 
    "24_495txt.zip", "19_48_txt.zip", "20_48_txt.zip", "21_48_txt.zip", "22_48_txt.zip", "23_48_txt.zip", "24_48_txt.zip", 
    "22_465txt.zip", "23_465txt.zip", "22_45_txt.zip", "23_45_txt.zip",
]
ELEVATION_FOLDER = Path("data/elevation")

def download_id_list():
    url = "http://www.dsr.inpe.br/topodata/data/txt"
    response = requests.get(url)
    id_list = re.findall(r'href="([^"]*\.zip)"', response.text)
    return id_list

# função para baixar e extrair o arquivo ZIP
def download_and_extract_zip(url, extract_to=ELEVATION_FOLDER):
    # Enviar uma solicitação HTTP GET para a URL
    response = requests.get(url)
    # Verifica se a solicitação foi bem-sucedida
    if response.status_code == 200:
        # Abrir o ZIP recebido na memória
        with zipfile.ZipFile(BytesIO(response.content)) as thezip:
            # Extrair o conteúdo do objeto ZIP para o diretório desejado
            thezip.extractall(path=extract_to)
            # Retorna a lista dos nomes dos arquivos extraídos
            return thezip.namelist()
    else:
        raise Exception(f"Erro ao baixar o arquivo: status code {response.status_code}")

def download_all():
    id_list = download_id_list()
    for id_ in tqdm(id_list, desc="Downloading files"):
        url = BASE_URL.format(sheet_id=id_)
        download_and_extract_zip(url)

def concat_all_files():
    file_list = [ELEVATION_FOLDER.joinpath(name) for name in os.listdir(ELEVATION_FOLDER)]
    df_list = []
    for file in tqdm(file_list, desc="Listing files"):
        df = pd.read_csv(file, sep="\s+")
        print("File:", file, "- Shape:", df.shape)
        df.columns = ["lat", "lon", "elevation"]
        for col in df.columns:
            df[col] = df[col].astype(float)
        df_list.append(df)
    coords_df = pd.concat(df_list, axis=0)
    print("Coords shape:", coords_df.shape)
    print(coords_df.head(5))
    coords_df.to_csv("data/saopaulo_state_elevation.csv", index=False)

def download_polygon_wkt(osmid):
    """
    Download polygon data from the OpenStreetMap service.
    
    Args:
        osmid (int): The OpenStreetMap ID for the desired polygon.
    
    Returns:
        str: WKT representation of the polygon or an error message.
    """
    base_url = 'https://polygons.openstreetmap.fr'
    response = requests.get(f"{base_url}/get_wkt.py", params={'id': osmid})
    
    if response.ok:
        return response.text
    else:
        return f"Error: Unable to download polygon for OSM ID {osmid}. HTTP Status: {response.status_code}"

if __name__ == "__main__":
    download_all()
    # concat_all_files()
    