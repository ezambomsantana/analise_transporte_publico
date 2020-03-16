import folium as folium
import geopandas as gpd
import numpy as np
import pandas as pd
import csv
import matplotlib.pyplot as plt
import unidecode
import math
import utm
from shapely.geometry import shape, LineString, Polygon
import matplotlib as mpl


folder_images_maps = "../images/"
folder_idosos_images_maps = "../idoso_images/"

mapa = gpd.GeoDataFrame.from_file("../data/shapes/Distritos_2017_region.shp", encoding='latin-1')
mapa = mapa.to_crs({"init": "epsg:4326"})
mapa['NomeDistri'] = mapa['NomeDistri'].apply(lambda x: unidecode.unidecode(x))

mapa = mapa[mapa['NumeroDist'] <=96]

folder_data = "../data/"
arq17 = "dados17.csv"

data17 = pd.read_csv(folder_data + arq17, dtype={'ZONA_O': str, 'ZONA_D': str}, header=0,delimiter=";", low_memory=False) 
data17 = data17.dropna(subset=['CO_O_X'])

data17 = data17.drop(['ID_DOM', 'FE_DOM', 'VIA_BICI','TP_ESTBICI','F_FAM','FE_FAM','FAMILIA','NO_MORAF',
                      'CONDMORA','QT_BANHO','QT_EMPRE','QT_AUTO','QT_MICRO','QT_LAVALOU','QT_GEL1'], axis=1)

data17['DISTANCE'] = 0

csv_file = folder_data + "regioes17.csv"
mydict = []
with open(csv_file, mode='r') as infile:
    reader = csv.reader(infile, delimiter=";")
    mydict = {rows[0]:rows[1] for rows in reader}

csv_file = folder_data + "distrito_pop.csv"
mydict_pop = []
with open(csv_file, mode='r') as infile:
    reader = csv.reader(infile, delimiter=";")
    mydict_pop = {rows[1]:rows[2] for rows in reader}

distritos_pop = pd.DataFrame.from_dict(mydict_pop, orient='index', columns=[ 'Populacao'])
print(distritos_pop)

distritos_pop['Populacao'] = distritos_pop['Populacao'].astype(float)

data17['NOME_O'] = data17['ZONA_O'].apply(lambda x: '' if pd.isnull(x) else mydict[x])
data17['NOME_D'] = data17['ZONA_D'].apply(lambda x: '' if pd.isnull(x) else mydict[x])

data17 = data17[data17['MOTIVO_D'].isin([1,2,3])] 

def load_districts(vehicle, orde, data):

    if vehicle != "0":
        vehicles = vehicle.split(",")
        vehicles_int = []
        for v in vehicles:
            vehicles_int.append(int(v))
        data17_copy = data[data['MODOPRIN'].isin(vehicles_int)] 
    
    data_mp2 = data17_copy[[orde,  'FE_VIA']].groupby([orde]).sum().sort_values(by=['FE_VIA']).reset_index()
    data_mp2 = data_mp2.set_index(orde)

    df = mapa.set_index('NomeDistri').join(data_mp2).join(distritos_pop)
    df = df.reset_index()

    return df

nomes = ["metro","trem","onibus","geral"]
tipos = ["1,3","2","4,5,6","1,2,3,4,5,6"]

# todos
for x in range(0, 4):

    tipo = tipos[x]
    nome = nomes[x]

    # Get the data about the districts, 15 is the number of the mode of the trip, bike in this case
    teste = load_districts(tipo, "NOME_O", data17)
    teste2 = teste.to_crs({'init': 'epsg:3857'})

    teste2['area'] = teste2['geometry'].area / 10**6
    teste2['densidade_area'] = teste['FE_VIA'] / teste2['area']
    teste2['densidade_pop'] = teste['FE_VIA'] / teste2['Populacao']

    cmap = mpl.cm.OrRd(np.linspace(0,1,20))
    cmap = mpl.colors.ListedColormap(cmap[10:,:-1])


    fig, ax = plt.subplots(1, 1)
    teste2.plot(column='FE_VIA', ax=ax, legend=True, cmap=cmap)

    plt.axis('off')
    plt.savefig(folder_images_maps + nome + '_quantidade_transporte.png', bbox_inches='tight', pad_inches=0.0)

    fig, ax = plt.subplots(1, 1)
    teste2.plot(column='densidade_area', ax=ax, legend=True, cmap=cmap)

    plt.axis('off')
    plt.savefig(folder_images_maps + nome + '_quantidade_transporte_densidade.png', bbox_inches='tight', pad_inches=0.0)

    fig, ax = plt.subplots(1, 1)
    teste2.plot(column='densidade_pop', ax=ax, legend=True, cmap=cmap)

    plt.axis('off')
    plt.savefig(folder_images_maps + nome + '_quantidade_transporte_densidade_populacao.png', bbox_inches='tight', pad_inches=0.0)

    teste2[['NomeDistri','densidade_area', 'FE_VIA','area','Populacao','densidade_pop']].to_csv('../generated_data/' + nome + '_transporte.csv')



for x in range(0, 4):

    tipo = tipos[x]
    nome = nomes[x]

    data17_idoso = data17[data17['IDADE'] >= 60]

    # Get the data about the districts, 15 is the number of the mode of the trip, bike in this case
    teste = load_districts(tipo, "NOME_O", data17_idoso)
    teste2 = teste.to_crs({'init': 'epsg:3857'})

    teste2['area'] = teste2['geometry'].area / 10**6
    teste2['densidade_area'] = teste['FE_VIA'] / teste2['area']
    teste2['densidade_pop'] = teste['FE_VIA'] / teste2['Populacao']

    cmap = mpl.cm.OrRd(np.linspace(0,1,20))
    cmap = mpl.colors.ListedColormap(cmap[10:,:-1])


    fig, ax = plt.subplots(1, 1)
    teste2.plot(column='FE_VIA', ax=ax, legend=True, cmap=cmap)

    plt.axis('off')
    plt.savefig(folder_idosos_images_maps + nome + '_quantidade_transporte.png', bbox_inches='tight', pad_inches=0.0)

    fig, ax = plt.subplots(1, 1)
    teste2.plot(column='densidade_area', ax=ax, legend=True, cmap=cmap)

    plt.axis('off')
    plt.savefig(folder_idosos_images_maps + nome + '_quantidade_transporte_densidade_area.png', bbox_inches='tight', pad_inches=0.0)

    fig, ax = plt.subplots(1, 1)
    teste2.plot(column='densidade_pop', ax=ax, legend=True, cmap=cmap)

    plt.axis('off')
    plt.savefig(folder_idosos_images_maps + nome + '_quantidade_transporte_densidade_populacao.png', bbox_inches='tight', pad_inches=0.0)


    teste2[['NomeDistri','densidade_area', 'FE_VIA','area','Populacao','densidade_pop']].to_csv('../idoso_generated_data/' + nome + '_transporte.csv')




