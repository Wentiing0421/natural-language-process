#!/usr/bin/env python
# coding: utf-8

import pandas as pd
import os
import requests, zipfile, io
import re
import datetime
import string
import time
import glob
from glob import iglob
from datetime import datetime
import newspaper
from newspaper import Article
import pickle
import csv
from langdetect import detect
from pickle_cleaning import *

def text_downloading(picklefilename):
    language_list = []
    with open(picklefilename,'rb') as PickleFiles:
        news_list = pickle.loads(PickleFiles.read())
    for story in news_list:
        story.clean_text()
        if story.get_text() == None:
            pass
        else:
            try:
                detect(story.text)
                language_list.append(detect(story.text))
                print(detect(story.text))
            except:
                print("error")
    return language_list

listru201402=text_downloading('ru201402.p')
listru201405=text_downloading('ru201405.p')
listru201408=text_downloading('ru201408.p')


df1 = pd.DataFrame(listru201402, columns=["colummn"])
df2 = pd.DataFrame(listru201405, columns=["colummn"])
df3 = pd.DataFrame(listru201408, columns=["colummn"])
df = pd.concat([df1,df2,df3])


def count_en (language_list,language):
    count=0
    for i in language_list:
        if i==language:
            count=count+1
    print('There are {} of total article, and {} of them are English article'.format(len(language_list),count))
    a=count/len(language_list)
    print('The percentage of English is {} of them are English'.format(a))


count_en(listru201402,'en')
unique_language_list = pd.unique(df['colummn'])
unique_language_list
len(unique_language_list)
def count(x):
    print(len(df.loc[df['colummn']==x])/len(df))
for i in unique_language_list:
    print(f'''
Percentage of language {i}''')
    count(i)
