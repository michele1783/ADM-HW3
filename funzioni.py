#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Nov  8 22:26:09 2021

@author: michele
"""
import requests
import lxml
import shutil
import urllib.request
import urllib.error as uer
import time
import nltk
import datetime
import csv
import os
import math
from tqdm import tqdm
from bs4 import BeautifulSoup
from pathlib import Path
import re
import pandas as pd
from nltk.corpus import stopwords
from string import punctuation
from nltk.stem.snowball import PorterStemmer
from nltk import stem
from nltk.tokenize import word_tokenize 
import json
import numpy
import heapq

url_file = 'urls.txt'
nFolders = 299
num_lines = sum(1 for line in open(url_file, encoding="utf-8")) 
pagesPerFolder = num_lines/nFolders
outputTSV = "dataset.tsv"
#retrieve url
def getUrl(lineNum, url_file):
    with open(url_file) as fp:
        for i, line in enumerate(fp):
            if i == lineNum-1:
                return line
            elif i >= lineNum:
                break

#download only a page
def downloadOneFile(pageNum):
    
    num_lines = sum(1 for line in open("urls.txt", encoding="utf-8"))
    pagesPerFolder = num_lines/nFolders
    url = getUrl(pageNum, "urls.txt")
    page = requests.get(url)
    soup = BeautifulSoup(page.content, features ="lxml")
    cartellaNumber = int(pageNum/(pagesPerFolder)) + 1
    print("Cartella" + str(cartellaNumber) + ".  Page_"+ str(pageNum))
    f = open("./cartelle/cartella{}".format(cartellaNumber) + "/page_{}.html".format(pageNum), "w",encoding="utf-8")
    f.write(soup.prettify())
    f.close()

#to retrieve the url and write urls.tx
def link_list(anime):
    with open('urls.txt', 'w') as file: #create the file urls.txt
        for page in range(0, anime+50, 50): 
            url = 'https://myanimelist.net/topanime.php?limit=' + str(page) #in each page there are 50 anime
            response = requests.get(url) 
            soup = BeautifulSoup(response.content) #get the page content
            ranking_list = soup.find_all(class_='ranking-list') #there is a table "ranking list"
            for l in ranking_list:
                link = l.find_all(class_='detail')[0].a['href'] #retrieving the link
                file.write("%s\n" % link) #write the url on the txt file 

#to download html page
def crawl(url_file):
    Path("directory").mkdir(exist_ok=True)
    for i in range(1,nFolders+1): #create 299 folders
        nomeCartella = 'cartelle/cartella{}'.format(i)  
        Path(nomeCartella).mkdir(exist_ok=True)
    num_lines = sum(1 for line in open(url_file, encoding="utf-8")) #number of lines of urls.txt
    pagesPerFolder = num_lines/nFolders #each folder will contain 64 pages
    
    c = 0
    lastFolder = 1
    
    with open(url_file, "r", encoding="utf-8") as a:
        for i in range(c): 
            print("skipping url: ", i)#this line is necessary to split the work between us. 
            #So we do not have to start from the beggining
            next(a)
        for i in a:
            page = requests.get(i)
            soup = BeautifulSoup(page.content, features ="lxml")
            number = int(c/(pagesPerFolder)) + 1 #it updates only after 64 pages per folder. It's the number of folder 
            #where it goes the page
            if number != lastFolder:
                print("I'm waiting") #we wait after a folder is completed
                lastFolder = number
                time.sleep(200)     #time sleep needed to avoid blocking by website       
            print("Going to save in cartella" + str(number) + ", the page " + str(c+1))
            f = open("./cartelle/cartella{}".format(number) + "/page_{}.html".format(c+1), "w",encoding="utf-8")
            f.write(soup.prettify())
            f.close()
#Some of our files were downloaded empty, with a size of circa 30kB. The page is downloaded correctly(200 as response)
#but the page are without information. 
            file_size = os.path.getsize("./cartelle/cartella{}/page_{}.html".format(number, c + 1)) #get the size of the page
            if file_size < 50000:
                os.remove("./cartelle/cartella{}/page_{}.html".format(number, c + 1)) #remove almost broken page
                page = requests.get(i) #redownload the page 
                soup = BeautifulSoup(page.content, features ="lxml")
                f = open("./cartelle/cartella{}".format(number) + "/page_{}.html".format(c+1), "w",encoding="utf-8")
                f.write(soup.prettify())
                f.close()

            else:
                c = c + 1
 
                
#used for the parsing of type
def findField(array, word):
    for x in array:
        if " ".join((x.find("span").text).split()) == word:
            return x
    return -1       


#used for the parsing
def extractData(pagePath):
    if os.path.isfile(pagePath):
        with open(pagePath, encoding="utf-8") as fp:
            soup = BeautifulSoup(fp, "html.parser")
            animeTitle = " ".join((soup.html.head.title.text.replace("- MyAnimeList.net", '')).split())

            #print("animeTitle: ", animeTitle)
            animeInfo = (soup.find_all("div",  attrs={ "class" : "spaceit_pad"}))
            #print("Animeinfo: ", animeInfo)

            aux = findField(animeInfo, "Type:")
            animeType = ""
            if aux.a != None:
                animeType = " ".join((aux.a.text).split())
            else:
                animeType = " ".join((findField(animeInfo, "Type:").findAll(text=True, recursive=False))).split()[0]
            #print("animeType :", animeType)

            numEpisodes = list(filter(lambda y: y != '',list(map(lambda x: " ".join((x).split()),findField(animeInfo, "Episodes:").findAll(text=True, recursive=False)) )))[0]
            animeNumEpisode = ""
            if numEpisodes.isdigit():
                animeNumEpisode = int(numEpisodes)
            #print("animeNumEpisode: ", animeNumEpisode)

            aired = list(filter(lambda y: y != '',list(map(lambda x: " ".join((x).split()),findField(animeInfo, "Aired:").findAll(text=True, recursive=False)) )))[0].split('to')
            if len(aired[0].split()) == 3:
                releaseDate = datetime.datetime(int(aired[0].split()[2]), months.index(aired[0].split()[0])+1 , int(aired[0].split()[1][:1]))
            else:
                releaseDate = ""
            if len(aired) == 2 and len(aired[1].split()) == 3:
                endDate = datetime.datetime(int(aired[1].split()[2]), months.index(aired[1].split()[0])+1 , int(aired[1].split()[1][:1]))
            else:
                endDate = ""
            #print("releaseDate: ", releaseDate)
            #print("endDate: ", endDate)

            animeNumMembers = int(list(filter(lambda y: y != '',list(map(lambda x: " ".join((x).split()),findField(animeInfo, "Members:").findAll(text=True, recursive=False)) )))[0].replace(",", ""))
            #print("animeNumMembers: ", animeNumMembers)
            
            animeScore = ""
            aux = soup.find_all("span", itemprop = "ratingValue")
            if aux != []:
                animeScore = float(" ".join((aux[0].text).split()))
            #print("animeScore: ", animeScore)

            animeUsers = -1
            aux = soup.find_all("span", itemprop = "ratingCount")
            if aux != []:
                animeUsers = int(" ".join((aux[0].text).split()))
            #print("animeUsers: ", animeUsers)

            animeRank = int(list(filter(lambda x: x[0] == '#',findField(animeInfo, "Ranked:").text.split()))[0].replace('#',''))
            #print("animeRank: ", animeRank)

            animePopularity = int(list(filter(lambda y: y != '',list(map(lambda x: " ".join((x).split()),findField(animeInfo, "Popularity:").findAll(text=True, recursive=False)) )))[0].replace("#", ""))
            #print("animePopularity: ", animePopularity)

            animeDescription = soup.find_all("p", itemprop = "description")[0].text.strip().replace('\n', '').replace('  ', '')
            #print("animeDescription: ", animeDescription)

            animeRelatedAHref = []
            if soup.find(name="table",attrs={"class":"anime_detail_related_anime"}) != None:
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
            
            aux = soup.find("link",  attrs={ "rel" : "canonical"})
            try:
                if aux != None:
                    url = aux.attrs['href']
                else:
                    url =  soup.find("meta",  attrs={ "property" : "og:url"})['content']
            except:
                url = ""

            return [animeTitle, animeType, animeNumEpisode, releaseDate, endDate, animeNumMembers, animeScore, animeUsers, animeRank, animePopularity, animeDescription, animeRelated, animeCharacters, animeVoices, animeStaff, url]
    return []


#used in order to generate the file .tsv
def tsvGenerator(): 
    c = 0
    with open(outputTSV, 'wt', encoding="utf-8") as out_file: #write a tsv file 
        tsv_writer = csv.writer(out_file, delimiter='\t')
        tsv_writer.writerow(["animeTitle", "animeType", "animeNumEpisode", "releaseDate", "endDate", "animeNumMembers", "animeScore", "animeUsers", "animeRank", "animePopularity", "animeDescription", "animeRelated", "animeCharacters", "animeVoices", "animeStaff"])
        for x in range(1, (num_lines-c) +1):

            number = int(c/(pagesPerFolder)) + 1
            path = "./cartelle/cartella{}".format(number) + "/page_{}.html".format(c+1)
            print("path: ", path)
            tsv_writer.writerow(extractData(path))
            c = c + 1

#used in order to clean the text
def cleaner(text):

    words = re.split(r'\W+', str(text))
    words = [word.lower() for word in words] #it deletes capital letter
    without_punct = [wp for wp in words if wp not in punctuation] #it removes punctuation
    sw = stopwords.words('english') #we specify the language, because stopwords change
    without_sw = [w for w in without_punct if w not in sw] 
    list_to_remove = ['b','br','span', 'one' , 'id', 'none'] #we don't want this words in our text
    clean_more = [w for w in without_sw if w not in list_to_remove] 
    
    
    ps = nltk.stem.PorterStemmer() 
    stemmed_list=[ps.stem(w) for w in clean_more ] #stemming
    return ' '.join(stemmed_list)


#used in order to create the file vocabulary.json
def create_vocabulary(data):
    ### Input == I use like input the dataset obtain where I apply the clean text function
    ### Output == I obtain a vocabulary, the keys are all tokens (with no repeat) contained in the animeDescription for the each rows
    ### for each token I define the index of the rows where the token is in the synopsis
    voc = {} 
    for i, row in data.iterrows(): 
            if len(data.at[i, "animeDescription"]) > 0:  # check if the list is empty or not to avoid the eventually error
                descr = data.at[i, "animeDescription"] #description of i-th anime 
                token = descr.split() 
                for word in token:
                    if word in voc.keys(): # insert the token into the vocabulary with the documents where this is present
                        if i not in voc[word]:
                            voc[word].append(i)
                    else:
                        voc[word] = [i]
    return voc

# create the inverted list according to the professors' requests
def create_inverted_list(vocabulary):
    inv_lst = {}
    indexes = list(vocabulary.keys()) # return the indexes list of the vocabulary
    for key in vocabulary.keys():
        term_id = indexes.index(key) # find the corresponding id from the vocabulary
        inv_lst[term_id] = vocabulary[key] # insert the list of documents into the inverted list
    
    return inv_lst

# map the interested word with corresponding term_id_i
def map_terms_id(vocabulary, cleanQString):
    # find each term_id
    term_id = []  # this is another function useful for mapping the term_id_i with the word into the vocabulary
    indexes = list(vocabulary.keys()) # return the indexes list of the vocabulary
    for token in cleanQString.split():
        try:
            term = indexes.index(token)
            term_id.append(term) # append the id that we want to make the score
        except:
            print(token + " is not in vocabulary")
    return term_id


# the search engine 1
def Search1(cleanQString, vocab, df, inv_lst):
    term_id = map_terms_id(vocab, cleanQString) # return the corresponding id of those terms

    # find the common documents where those terms are present
    intersection_list = []
    for term in term_id:
        if not intersection_list:
            intersection_list = inv_lst[term] 
            # if the intersection list is empty insert the first list of the first token
        else:
            intersection_list = set(intersection_list).intersection(set(inv_lst[term])) 
            # make the intersection, this respect the properties of the sets

    new_df = pd.DataFrame(columns=['animeTitle', 'animeDescription', 'Url']) # create the new dataset according to the professors' requests
    for row in intersection_list:
        #append row to the dataframe
        #we have parsed also the url
        new_row = {'animeTitle': df.loc[row, "animeTitle"], 'animeDescription': df.loc[row, "animeDescription"], 'Url': df.loc[row, "Url"]}
        new_df = new_df.append(new_row, ignore_index=True)
        
    return new_df

#used in order to create the second inverted index
def inverted_list_2(voc, df):
    #The vocabulary defined in function create_vocabulary
    ### Output == A new inverted list contained like keys all of token in the vocabulary but with the index and for each keys I have a list of tuples..
    ### The first value of tuple is the document where I can find this token and the second value is tfidf for the token in this document
    inv_lst2 = {}

    indexes = list(voc.keys()) #all keys of the vocabulary
    for key in voc.keys():#check every key
        lst_doc = voc[key] #docs for that keys 

        result = []

        for doc in lst_doc: # extract the list of tokens from anime description
            interested_row = df.at[doc, "animeDescription"]


            tf = interested_row.count(key) / len(interested_row) #time frequencies of each key

            idf = math.log(len(df)/len(lst_doc)) #Inverse Document Frequency

            tf_idf = round(tf * idf, 3) 

            result.append([doc,tf_idf])

        inv_lst2[indexes.index(key)] = result # insert the result into the inverted list

    return inv_lst2

#used in order to compute tf-idf of the query
def queries(query):
#our query
    indexes = list(vocabulary.keys())
    query = query.split() 
    query_score = []
    for key in query: #for each token in our query, not anymore all token 
        try:
            lst_doc = vocabulary[key] # retrieve the pages

            tf = query.count(key) / len(query) #tf of the i-th word 

            idf = math.log(len(data)/len(lst_doc)) #idf of the i-th word 

            tf_idf = round(tf * idf, 3) 

            query_score.append([key, tf_idf])
    
        except:
            print("there is not "+ key)

    return(query_score)

#used in order to retrieve docs where there are all words of the query
def documents(cleanQString, vocab, df, inv_lst):
    term_id = map_terms_id(vocab, cleanQString) # return the corresponding id of those terms

    # find the common documents where those terms are present
    intersection_list = []
    for term in term_id:
        if not intersection_list:
            intersection_list = inv_lst[term] #if the intersection list is empty insert the first list of the first token
        else:
            intersection_list = set(intersection_list).intersection(set(inv_lst[term]))
    return list(intersection_list)

#used in order to the norm of query 
def qnorma(query_score): #compute the norm of the query
    q_norm = []
    for i in range(len(query_score)):
        q_norm.append((query_score[i][1])**2) #compute the square
    q_norm_2 = 0  
    for i in range(len(query_score)):
        q_norm_2 += q_norm[i] #sum them
    q_norm = math.sqrt(q_norm_2) #compute the square root
    return(q_norm)

#used for the last point
def Search3(cleanQString, vocab, df, inv_lst):
    term_id = fun.map_terms_id(vocab, cleanQString) # return the corresponding id of those terms

    # find the common documents where those terms are present
    intersection_list = []
    for term in term_id:
        if not intersection_list:
            intersection_list = inv_lst[term] 
            # if the intersection list is empty insert the first list of the first token
        else:
            intersection_list = set(intersection_list).intersection(set(inv_lst[term])) 
            # make the intersection, this respect the properties of the sets

    new_df = pd.DataFrame(columns=['animeTitle', 'animeDescription', 'Url']) # create the new dataset according to the professors' requests
    for row in intersection_list:
        #append row to the dataframe
        #we have parsed also the url
        new_row = {'animeTitle': df.loc[row, "animeTitle"], 'animeDescription': df.loc[row, "animeDescription"], 'Url': df.loc[row, "Url"],\
                  'animeScore': df.loc[row, "animeScore"], 'animeRank': df.loc[row, "animeRank"]}
        new_df = new_df.append(new_row, ignore_index=True)
        
    return new_df