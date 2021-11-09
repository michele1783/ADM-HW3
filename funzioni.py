#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Nov  8 22:26:09 2021

@author: michele
"""
import shutil
from bs4 import BeautifulSoup
import datetime
from pathlib import Path
import requests
from tqdm import tqdm
import time
import nltk
from nltk.corpus import stopwords
from nltk.stem.snowball import PorterStemmer
from nltk.tokenize import RegexpTokenizer
months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun','Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

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
    anime = list(set(anime))
    with open('urls.txt', 'w') as f:
        for item in tqdm(anime):
            f.write("%s\n" % item)  
            
def crawl(url_file):
    Path("directory").mkdir(exist_ok=True)
    for i in range(1,nFolders+1):
        nomeCartella = 'cartella{}'.format(i)
        Path(nomeCartella).mkdir(exist_ok=True)
    num_lines = sum(1 for line in open(url_file))
    pagesPerFolder = num_lines/nFolders
    a = open(url_file, "r")
    c = 0
    lastFolder = 200
    for i in a:
        page = requests.get(i)
        soup = BeautifulSoup(page.content, features ="lxml")
        number = int(c/(pagesPerFolder)) + 1
        if number != lastFolder:
            print("I'm waiting")
            lastFolder = number
            time.sleep(300)            
        print("Going to save in cartella" + str(number) + ", the page " + str(c+1))
        f = open("./cartella{}".format(number) + "/page_{}.html".format(c+1), "w",encoding="utf-8")
        f.write(soup.prettify())
        f.close()
        c = c + 1
        
def findField(array, word):
    for x in array:
        #print("#####################################")
        #print(" ".join((x.find("span").text).split()))
        #print("#####################################")
        if " ".join((x.find("span").text).split()) == word:
            return x
    return -1       
        
        
def cleaner(text):
    stop_words = set(stopwords.words('english')) # retrieve stop words
    tokenizer = RegexpTokenizer("[\w']+") # recognize the tokens
    parole = tokenizer.tokenize(text) # tokenize the text
    correct_words = [] # save the correct words to consider like tokens
    for word in parole:
        # check if the word is lower and it isn't a stop word or a number
        if word.lower() not in stop_words and word.isalpha(): 
            word = PorterStemmer().stem(word) # use the stemmer function
            correct_words.append(word.lower()) # insert the good token to lower case
        
    return correct_words

def create_vocabulary(data):
    ### Input == I use like input the dataset obtain in exercise 1 where i apply the clean text function
    ### Output == I obtain a vocabulary, the keys are all tokens (with no repeat) contained in the synopsis for the each rows
    ### for each token I define the index of the rows where the token is in the synopsis
    voc = {}
    for i, row in data.iterrows():
            if len(data.at[i, "Synopsis"]) > 0:  # check if the list is empty or not to avoid the eventually error
                for word in data.at[i, "Synopsis"]: # bring the token from the list
                    if word in voc.keys(): # insert the token into the vocabulary with the documents where this is present
                        if i not in voc[word]:
                            voc[word].append(i)
                    else:
                        voc[word] = [i]
    return voc

def extractData(pagePath):
    with open(pagePath, encoding="utf-8") as fp:
        soup = BeautifulSoup(fp, "html.parser")
        animeTitle = " ".join((soup.html.head.title.text).split())
        
        #print("animeTitle: ", animeTitle)
        animeInfo = (soup.find_all("div",  attrs={ "class" : "spaceit_pad"}))
        #print("Animeinfo: ", animeInfo)
        
        animeType = " ".join((findField(animeInfo, "Type:").a.text).split())
        #print("animeType :", animeType)
        
        animeNumEpisode = int(list(filter(lambda y: y != '',list(map(lambda x: " ".join((x).split()),findField(animeInfo, "Episodes:").findAll(text=True, recursive=False)) )))[0])
        #print("animeNumEpisode: ", animeNumEpisode)
        
        aired = list(filter(lambda y: y != '',list(map(lambda x: " ".join((x).split()),findField(animeInfo, "Aired:").findAll(text=True, recursive=False)) )))[0].split('to')
        releaseDate = datetime.datetime(int(aired[0].split()[2]), months.index(aired[0].split()[0])+1 , int(aired[0].split()[1][:1]))
        if len(aired) == 2:
            endDate = datetime.datetime(int(aired[1].split()[2]), months.index(aired[1].split()[0])+1 , int(aired[1].split()[1][:1]))
        else:
            endDate = ""
        #print("releaseDate: ", releaseDate)
        #print("endDate: ", endDate)
        
        animeNumMembers = int(list(filter(lambda y: y != '',list(map(lambda x: " ".join((x).split()),findField(animeInfo, "Members:").findAll(text=True, recursive=False)) )))[0].replace(",", ""))
        #print("animeNumMembers: ", animeNumMembers)
        
        animeScore = float(" ".join((soup.find_all("span", itemprop = "ratingValue")[0].text).split()))
        #print("animeScore: ", animeScore)
        
        animeUsers = int(" ".join((soup.find_all("span", itemprop = "ratingCount")[0].text).split()))
        #print("animeUsers: ", animeUsers)
        
        animeRank = int(list(filter(lambda x: x[0] == '#',findField(animeInfo, "Ranked:").text.split()))[0].replace('#',''))
        #print("animeRank: ", animeRank)

        animePopularity = int(list(filter(lambda y: y != '',list(map(lambda x: " ".join((x).split()),findField(animeInfo, "Popularity:").findAll(text=True, recursive=False)) )))[0].replace("#", ""))
        #print("animePopularity: ", animePopularity)
        
        animeDescription = soup.find_all("p", itemprop = "description")[0].text.strip().replace('\n', '').replace('  ', '')
        #print("animeDescription: ", animeDescription)
        
        animeRelatedAHref = soup.find(name="table",attrs={"class":"anime_detail_related_anime"}).findChildren('a', href=True)
        animeRelated = []
        for x in animeRelatedAHref:
            aux = " ".join((x.text).split())
            if aux not in animeRelated:
                animeRelated.append(aux)
        #print("animeRelated: ", animeRelated)
        
        animeCharactersRaw = soup.find_all("h3", attrs={"class" : "h3_characters_voice_actors"})
        animeCharacters = []
        for x in animeCharactersRaw:
            animeCharacters.append(" ".join((x.text).split()))
        #print("animeCharacters: ", animeCharacters)
        
        animeVoicesRaw = soup.find_all("td", attrs={"class" : "va-t ar pl4 pr4"})
        animeVoices = []
        for x in animeVoicesRaw:
            animeVoices.append(" ".join((x.contents[1].text).split()))
        #print("animeVoices: ", animeVoices)
        
        animeStaff = ""
        if(len(soup.find_all("div", attrs={"class" : "detail-characters-list clearfix"})) == 2):
            aux = soup.find_all("div", attrs={"class" : "detail-characters-list clearfix"})[1]
            animeStaffRaw = []
            for x in aux.findChildren('a'):
                if (" ".join((x.text).split()) != ''):
                    animeStaffRaw.append(" ".join((x.text).split()))
            animeStaffTaskRaw = []
            for x in aux.findChildren('small'):
                animeStaffTaskRaw.append(" ".join((x.text).split()))
            #print("animeStaffRaw: ", animeStaffRaw)
            #print("animeStaffTaskRaw: ", animeStaffTaskRaw)
            animeStaff = [list(a) for a in zip(animeStaffRaw, animeStaffTaskRaw)]

        
        #print("animeStaff: ", animeStaff)
        
        return [animeTitle, animeType, animeNumEpisode, releaseDate, endDate, animeNumMembers, animeScore, animeUsers, animeRank, animePopularity, animeDescription, animeRelated, animeCharacters, animeVoices, animeStaff]
    
    
    
def extractData(pagePath):
    with open(pagePath, encoding="utf-8") as fp:
        soup = BeautifulSoup(fp, "html.parser")
        
        try:
            animeTitle = " ".join((soup.html.head.title.text.replace("- MyAnimeList.net", '')).split())
        except:
            animeTitle = " "
        #print("animeTitle: ", animeTitle)
        
        try:
            animeInfo = (soup.find_all("div",  attrs={ "class" : "spaceit_pad"}))
        #print("Animeinfo: ", animeInfo)
        except:
            animeInfo = " "
        
        try:
            animeType = " ".join((findField(animeInfo, "Type:").a.text).split())
        #print("animeType :", animeType)
        except:
            animeType = " "
        try:
            animeNumEpisode = int(list(filter(lambda y: y != '',list(map(lambda x: " ".join((x).split()),findField(animeInfo, "Episodes:").findAll(text=True, recursive=False)) )))[0])
        #print("animeNumEpisode: ", animeNumEpisode)
        except:
            animeNumEpisode = " "
        
        try:
            aired = list(filter(lambda y: y != '',list(map(lambda x: " ".join((x).split()),findField(animeInfo, "Aired:").findAll(text=True, recursive=False)) )))[0].split('to')
            releaseDate = datetime.datetime(int(aired[0].split()[2]), months.index(aired[0].split()[0])+1 , int(aired[0].split()[1][:1]))
            if len(aired) == 2:
                endDate = datetime.datetime(int(aired[1].split()[2]), months.index(aired[1].split()[0])+1 , int(aired[1].split()[1][:1]))
            else:
                endDate = ""
        except:
            releaseDate = " "
            endDate = " "
        #print("releaseDate: ", releaseDate)
        #print("endDate: ", endDate)
        
        try:
            animeNumMembers = int(list(filter(lambda y: y != '',list(map(lambda x: " ".join((x).split()),findField(animeInfo, "Members:").findAll(text=True, recursive=False)) )))[0].replace(",", ""))
        #print("animeNumMembers: ", animeNumMembers)
        except:
            animeNumMembers = " "
        
        try:
            animeScore = float(" ".join((soup.find_all("span", itemprop = "ratingValue")[0].text).split()))
        #print("animeScore: ", animeScore)
        except:
            animeScore = " "

        try:
            animeUsers = int(" ".join((soup.find_all("span", itemprop = "ratingCount")[0].text).split()))
        #print("animeUsers: ", animeUsers)
        except:
            animeUsers = " "
        
        try:
            animeRank = int(list(filter(lambda x: x[0] == '#',findField(animeInfo, "Ranked:").text.split()))[0].replace('#',''))
        #print("animeRank: ", animeRank)
        except:
            animeRank = " "
        
        try:
            animePopularity = int(list(filter(lambda y: y != '',list(map(lambda x: " ".join((x).split()),findField(animeInfo, "Popularity:").findAll(text=True, recursive=False)) )))[0].replace("#", ""))
        #print("animePopularity: ", animePopularity)
        except:
            animePopularity = " "
        
        try:
            animeDescription = soup.find_all("p", itemprop = "description")[0].text.strip().replace('\n', '').replace('  ', '')
        #print("animeDescription: ", animeDescription)
        except:
            animeDescription = " "
        
        try:
            animeRelatedAHref = soup.find(name="table",attrs={"class":"anime_detail_related_anime"}).findChildren('a', href=True)
            animeRelated = []
            for x in animeRelatedAHref:
                aux = " ".join((x.text).split())
            if aux not in animeRelated:
                animeRelated.append(aux)
        #print("animeRelated: ", animeRelated)
        except:
            animeRelated = " "
        
        try:
            animeCharactersRaw = soup.find_all("h3", attrs={"class" : "h3_characters_voice_actors"})
            animeCharacters = []
            for x in animeCharactersRaw:
                animeCharacters.append(" ".join((x.text).split()))
        #print("animeCharacters: ", animeCharacters)
        except:
            animeCharacters = " "

        try:
            animeVoicesRaw = soup.find_all("td", attrs={"class" : "va-t ar pl4 pr4"})
            animeVoices = []
            for x in animeVoicesRaw:
                animeVoices.append(" ".join((x.contents[1].text).split()))
        #print("animeVoices: ", animeVoices)
        except:
            animeVoices = " "


        try:
            animeStaff = ""
            if(len(soup.find_all("div", attrs={"class" : "detail-characters-list clearfix"})) == 2):
                aux = soup.find_all("div", attrs={"class" : "detail-characters-list clearfix"})[1]
                animeStaffRaw = []
            for x in aux.findChildren('a'):
                if (" ".join((x.text).split()) != ''):
                    animeStaffRaw.append(" ".join((x.text).split()))
            animeStaffTaskRaw = []
            for x in aux.findChildren('small'):
                animeStaffTaskRaw.append(" ".join((x.text).split()))
            #print("animeStaffRaw: ", animeStaffRaw)
            #print("animeStaffTaskRaw: ", animeStaffTaskRaw)
            animeStaff = [list(a) for a in zip(animeStaffRaw, animeStaffTaskRaw)]
        except:
            animeStaff = " "

        
        #print("animeStaff: ", animeStaff)
        
        return [animeTitle, animeType, animeNumEpisode, releaseDate, endDate, animeNumMembers, animeScore, animeUsers, animeRank, animePopularity, animeDescription, animeRelated, animeCharacters, animeVoices, animeStaff]
        
        
        
        