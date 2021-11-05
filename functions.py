#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Nov  5 09:16:45 2021

@author: michele
"""


import shutil
from bs4 import BeautifulSoup
from pathlib import Path
import requests
from tqdm import tqdm
import time

nFolders = 200

def crawl(url_file):
    Path("directory").mkdir(exist_ok=True)
    for i in range(1,nFolders+1):
        nomeCartella = 'cartella{}'.format(i)
        Path(nomeCartella).mkdir(exist_ok=True)
    num_lines = sum(1 for line in open(url_file))
    pagesPerFolder = num_lines/nFolders
    a = open(url_file, "r")
    c = 900
    lastFolder = 1
    for i in a: 
        page = requests.get(i)
        soup = BeautifulSoup(page.content, features ="lxml")
        number = int(c/(pagesPerFolder)) + 1
        if number != lastFolder:
            lastFolder = number
            time.sleep(120)            
        f = open("./cartella{}".format(number) + "/page_{}.html".format(c+1), "w",encoding="utf-8")
        f.write(soup.prettify())
        f.close()
        c = c + 1

def get_urls(init_url, number_pages):
    anime = []
    for page in tqdm(range(0,number_pages)):
        url = init_url +str(page *50)
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")
        for tag in soup.find_all("tr"):#cerco le righe della tabella
            links = tag.find_all("a")
            for link in links:
                if type(link.get("id")) == str and len(link.contents[0]) >1:
                    anime.append((link.get("href")))
    
    with open('urls.txt', 'w') as f:
        for item in tqdm(anime):
            f.write("%s\n" % item)  