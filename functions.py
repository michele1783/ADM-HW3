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
    
def crawl(url_file):
    Path("directory").mkdir(exist_ok=True)
    for i in range(1,5):
        nomeCartella = 'cartella{}'.format(i)
        Path(nomeCartella).mkdir(exist_ok=True)
    a = open(url_file, "r")
    c = 0
    number = 1
    for i in a:
        c = c + 1 
        page = requests.get(i)
        soup = BeautifulSoup(page.content, features ="lxml")
        f = open("page_{}.html".format(c), "w")
        f.write(soup.prettify())
        if c <= 5000:
            number = 1
        elif (c > 5000 and c <= 10000):
            number = 2
        elif (c > 10000 and c <= 15000):
            number = 3
        elif (c > 15000 and c <= 20000):
            number = 4
        shutil.move("page_{}.html".format(c), "/Users/michele/ADM2021/cartella{}".format(number))
        f.close()