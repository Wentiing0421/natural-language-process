import pandas as pd
import numpy as np
import os
import requests, zipfile, io
import re
import string
import time
import glob
from glob import iglob
from newspaper import Article
from datetime import datetime
import pickle
import csv
from langdetect import detect
from time import ctime

def process(df): #input filename
    """
    Fetches news items from csv file
    Returns a list of News.
    """
    ret = []
    for index,row in df.iterrows():
        sqldate = row['SQLDATE']
        month_year = row['MonthYear']
        goldstein_scale = row['GoldsteinScale']
        num_mentions = row['NumMentions']
        num_sources = row['NumSources']
        num_articles = row['NumArticles']
        tone = row['AvgTone']
        url = row['SOURCEURL']
        news = News(sqldate, month_year, goldstein_scale, num_mentions, num_sources, num_articles, tone, url)
        ret.append(news)
    print('\nThere are %d items in News.'% len(ret))
    return ret

def removeDuplicate (df):
    date=df.sort_values(by='SQLDATE', ascending=True).groupby('SOURCEURL').first() ["SQLDATE"].reset_index().drop(['SOURCEURL'],axis=1)
    by_data=df.groupby('SOURCEURL')['MonthYear','GoldsteinScale','NumMentions','NumSources','NumArticles','AvgTone'].mean().reset_index()
    by_data['SQLDATE']=date
    return by_data

class News:
    def __init__(self, sqldate, month_year, goldstein_scale, num_mentions, num_sources, num_articles, tone, url):
        self.sqldate = sqldate
        self.month_year = month_year
        self.goldstein_scale = goldstein_scale
        self.num_mentions = num_mentions
        self.num_sources = num_sources
        self.num_articles = num_articles
        self.tone = tone
        self.url = url
        self.text = None
        self.publish_date = None
        self.taxonomy = []
        self.language = []

    def get_sqldate(self):
        return self.sqldate
    def get_monthyear(self):
        return self.month_year
    def get_goldsteinscale(self):
        return self.goldstein_scale
    def get_nummentions(self):
        return self.num_mentions
    def get_numsources(self):
        return self.num_sources
    def get_numarticles(self):
        return self.num_articles
    def get_tone(self):
        return self.tone
    def get_url(self):
        return self.url
    def get_text(self):
        return self.text
    def get_publish_date(self):
        return self.publish_date
    def get_taxonomy(self):
        return self.taxonomy
    def set_taxonomy(self,taxonomy):
        self.taxonomy.extend(taxonomy)
    def get_language(self):
        return self.language
    def set_language(self,language):
        self.language.extend(language)
    def clean_text(self):
        try:
            article = Article(self.url)
            article.download()
            article.parse()
            self.text,self.publish_date = article.text, article.publish_date
            print('Success.')
        except:
            self.text,self.publish_date = None, None
            print('No text found.')


# # Use these functonto save data to pickle

# ### csvfilename:the csv file we downlaod(after sorting and seperate by month). for example: uk201606.csv
# ### picklefilename:the name for pickle file. for example: uk201606data.p
# In[ ]:


def pickle_cleaning(csvfilename,picklefilename):
    data = removeDuplicate(pd.read_csv(csvfilename))
    news_list = process(data)#change to class
    pickle.dump(news_list, open(picklefilename,'wb'))#save as pickle
    print(len(data))
