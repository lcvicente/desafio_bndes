# -*- coding: utf-8 -*-
"""
Created on Mon Aug  9 08:56:49 2021

@author: Leonardo
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd

MAIN_URL = "https://dadosabertos.bndes.gov.br"
GROUP_URL = MAIN_URL + "/group"

list_data = []
r = requests.get(GROUP_URL)
soup = BeautifulSoup(r.text, 'html.parser')

list_href_grupos = soup.find_all('a', attrs={'class': 'media-view'})

for href_grupo in list_href_grupos:
    url_conjunto = href_grupo['href']
    url_conjunto = MAIN_URL + url_conjunto
    print(url_conjunto)

    r = requests.get(url_conjunto)
    soup = BeautifulSoup(r.text, 'html.parser')

    
    list_csv_files = soup.find_all('a', attrs={'class': 'label-default', 'data-format': 'csv'})
    list_nome_conj = soup.find_all('h3')
    list_nome_conj  = [item.text.replace("\n", "").strip() for item in list_nome_conj]
    
    for nome_conj, csv_file in zip(list_nome_conj, list_csv_files):
        print(nome_conj)
        
        url_dataset = csv_file['href']
        url_dataset = MAIN_URL + url_dataset
        
        r = requests.get(url_dataset)
        soup = BeautifulSoup(r.text, 'html.parser')
        
        # Lista os datasets (PDF e CSV)
        list_datasets = soup.find_all('li', attrs={'class': 'resource-item'})
        
        for dataset in list_datasets:
            # Verifica se é CSV
            csv = dataset.find('span', attrs={'data-format': 'csv'})
            if csv == None:
                continue
            # Verifica o título
            title = dataset.find('a', attrs={'class': 'heading'}).get('title')
            
            # Verifica o link para o arquivo
            list_links = dataset.find_all('a')
            link_csv = None
            for link in list_links:
                if ".csv" in link['href']:
                    link_csv = link['href']
                    print(title)
                    print(link_csv)
                    list_data.append([nome_conj, title, link_csv])
                    break
                

df_colet = pd.DataFrame(columns=['conjunto', 'dataset', 'link'], data=list_data)

df_colet.drop_duplicates(inplace=True)

df_colet['row_count'] = 0
df_colet['col_count'] = 0

df_columns = pd.DataFrame()
for idx in df_colet.index:
    conjunto, dataset, link = df_colet.loc[idx, ['conjunto', 'dataset', 'link']].values
    print(dataset)
    df = pd.read_csv(link, sep=";", decimal=",", encoding="UTF-8")
    df_col = pd.DataFrame(columns=['nome_col'], data=df.columns.values)
    df_col['conjunto'] = conjunto
    df_col['dataset'] = dataset
    df_columns = pd.concat([df_col, df_columns])
    df_colet.loc[idx, ['row_count', 'col_count']] = df.shape
    
    
df_columns = df_columns[['conjunto', 'dataset', 'nome_col']].copy()

# Exporta
writer = pd.ExcelWriter("metadados.xlsx", engine="xlsxwriter")
df_colet.to_excel(writer, sheet_name="datasets", index=False)
df_columns.to_excel(writer, sheet_name="colunas", index=False)
writer.save()
