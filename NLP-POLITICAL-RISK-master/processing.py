# -*- coding: utf-8 -*-
"""
Created on Mon Sep  2 16:07:52 2019

@author: shen yanzi
"""

import pandas as pd
import numpy as np
from newspaper import Article
import pickle
from langdetect import detect
import multiprocessing as mp
import time
import datetime
import string


def process(csvfile): #input filename
    """
    Fetches news items from csv file
    Returns a list of News class
    """
    df = pd.read_csv(csvfile)
    #remove duplicate url
    df = df.groupby('SOURCEURL')['SQLDATE','MonthYear','GoldsteinScale','NumMentions','NumSources','NumArticles','AvgTone']\
    .mean().sort_values(by='SQLDATE').reset_index()
    
    news_list = []
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
        news_list.append(news)

    print('There are {} items in News.'.format(len(news_list)))
    return news_list


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
        self.language.append(language)
    def clean_text(self):
        article = Article(self.url)
        try:
            article.download()
            article.parse()
            self.text,self.publish_date = article.text, article.publish_date
            #print('Success.')
        except:
            self.text,self.publish_date = None, None
            #print('No text found.')
            
            
def text_downloading(csvfile, picklefile):
    news_list = process(csvfile) 
    
    start = time.time()
    print('Start time:',str(datetime.datetime.now()))
    
    for news in news_list:
        news.clean_text()
        if news.get_text() == None:
            pass
        else:
            try:
                language = detect(news.get_text())
                news.set_language(language)
            except:
                pass
    
    file = open(picklefile,'wb')        
    pickle.dump(news_list, file)
    
    print("End time:",str(datetime.datetime.now()))
    print("Time used:",(time.time() - start))

######################
 
class Trigger:
    def evaluate(self, news):
        """
        Returns True if an alert should be generated
        for the given news item, or False otherwise.
        """
        # DO NOT CHANGE THIS!
        raise NotImplementedError
        
class PhraseTrigger(Trigger):
    def __init__(self, phrase):
        self.phrase = phrase
        
    def get_phrase(self):
        return self.phrase
    
    def evaluate(self, news):
        return self.is_phrase_in(news)
    
    def is_phrase_in(self, text):
        raw_text = text.lower()
        raw_phrase = self.phrase.lower()
        for char in raw_text:
            if char in string.punctuation:
                raw_text = raw_text.replace(char,' ')
        raw_list = raw_text.split()
        phrase_list = raw_phrase.split()
        
        if phrase_list[0] not in raw_list:
            return False
        else:
            temp_index = raw_list.index(phrase_list[0])
            return phrase_list == raw_list[temp_index:temp_index + len(phrase_list)]

class TextTrigger(PhraseTrigger):
    def __init__(self, phrase):
        PhraseTrigger.__init__(self, phrase)
        
    def get_phrase(self):
        return self.phrase

    def get_args(self):
        return self.phrase
        
    def evaluate(self, news):
        return self.is_phrase_in(news.get_text())

class AndTrigger(Trigger):
    def __init__(self, *args):
        self.args = args
        
    def get_args(self):
        phrase_list = [arg.get_phrase() for arg in self.args]
        return '+'.join(phrase_list)
    
    def evaluate(self, news):
        true_list = [T.evaluate(news) for T in self.args]  
        result = [True, False][False in true_list]
        return result
    
    
###################
    
def read_trigger_config(filename):
    """
    filename: the name of a trigger configuration file

    Returns: a list of trigger objects specified by the trigger configuration
        file.
    """
    
    trigger_file = open(filename, 'r', encoding='utf-8')
    lines = []
    for line in trigger_file:
        line = line.rstrip()
        if not (len(line) == 0 or line.startswith('//')):
            lines.append(line)

    trigger_dict = {}
    
    for line in lines:
        l_item = line.split('+')
        if l_item[1] == 'TEXT':
            trigger_dict[l_item[0]] = TextTrigger(l_item[2])
        elif l_item[1] == 'AND':
            arg_tuple = tuple(TextTrigger(item) for item in l_item[2:])
            trigger_dict[l_item[0]] = AndTrigger(*arg_tuple)
            
    return trigger_dict 
   
def filter_stories(inputpickle,trigger_dict_eng,trigger_dict_span,outputpickle):
    start = time.time()
    print("Start time:",str(datetime.datetime.now()))
    
    file = open(inputpickle,'rb')
    news_list = pickle.loads(file.read())
    
    for news in news_list:    
        if news.get_language() != []:
            if news.get_language()[0] == 'en':
                for key,trig in trigger_dict_eng.items():
                    try:
                        news.set_taxonomy((key,trig.get_args())) if trig.evaluate(news)                     else time.ctime()#print('False',end=' ')
                    except AttributeError:
                        pass   
            if news.get_language()[0] == 'es':
                for key,trig in trigger_dict_span.items():
                    try:
                        news.set_taxonomy((key,trig.get_args())) if trig.evaluate(news)                     else time.ctime()#print('False',end=' ')
                    except AttributeError:
                        pass
                    
        if news.get_taxonomy() != []:
            print(news.get_language())
            print(news.get_taxonomy()) 
            
    print("End time:",str(datetime.datetime.now()))
    print("Time used:",(time.time() - start))
    
    pickle.dump(news_list, open(outputpickle,'wb'))

###############################################

def count(picklefile):
    url,sqldate,goldstein_scale,num_mentions,num_articles,tone,taxonomy,language = \
    [],[],[],[],[],[],[],[]

    file = open(picklefile,'rb')
    news_list = pickle.loads(file.read())
    for news in news_list:
        url.append(news.url)
        sqldate.append(news.sqldate)
        goldstein_scale.append(news.goldstein_scale)
        num_mentions.append(news.num_mentions)
        num_articles.append(news.num_articles)
        tone.append(news.tone)
        taxonomy.append(news.taxonomy)
        language.append(news.language)

    original=pd.DataFrame({"URL":url, 
                        "date":sqldate, 
                        "goldstein_scale":goldstein_scale, 
                        "num_mentions":num_mentions, 
                        "num_articles":num_articles, 
                         "tone":tone, 
                         "taxonomy":taxonomy, 
                         "language":language}).sort_values('date')  

    original['language'] = original['language'].apply(lambda x:x[0] if (x!=[]) else np.NaN )
    
    final=pd.DataFrame()
    final['NumUniqueUrl'] = original.groupby('date')['URL'].count()
    final['NumUniqueUrl'] .fillna(0)
    final['NumUniqueUrlwithArticle'] = original.groupby('date')['language'].apply(lambda x: x.notnull().sum())
    final['NumUniqueUrlwithArticle'].fillna(0)
    final['MeanToneAllAll'] = original.groupby('date')['tone'].mean()
    final['StdToneAllAll'] = original.groupby('date')['tone'].std()
    
    final['NumToneAllSpan'] = original.groupby('date')['language'].apply(lambda x: (x=='es').sum())# if language=[es]
    final['NumToneAllSpan'] = final['NumToneAllSpan'].fillna(0)
    final['MeanToneAllSpan'] =original[original['language']=='es'].groupby('date')['tone'].mean()
    final['StdToneAllSpan'] = original[original['language']=='es'].groupby('date')['tone'].std()
    
    final['NumToneAllEng'] = original.groupby('date')['language'].apply(lambda x: (x=='en').sum())
    final['NumToneAllEng'] = final['NumToneAllEng'].fillna(0)
    final['MeanToneAllEng'] = original[original['language']=='en'].groupby('date')['tone'].mean()
    final['StdToneAllEng'] = original[original['language']=='en'].groupby('date')['tone'].std()
    
    #full
    final['NumToneFullLan'] = original[((original['language']=='en')|(original['language']=='es'))&(original['taxonomy'].map(lambda d: len(d)) > 0)]\
    .groupby('date')['tone'].count()
    final['NumToneFullLan'] = final['NumToneFullLan'].fillna(0)
    final['MeanToneFullLan'] = original[((original['language']=='en')|(original['language']=='es'))&(original['taxonomy'].map(lambda d: len(d)) > 0)]\
    .groupby('date')['tone'].mean()
    final['StdToneFullLan'] = original[((original['language']=='en')|(original['language']=='es'))&(original['taxonomy'].map(lambda d: len(d)) > 0)]\
    .groupby('date')['tone'].std()
    
    final['NumToneFullSpan'] = original[(original['language']=='es')&(original['taxonomy'].map(lambda d: len(d)) > 0)]\
    .groupby('date')['tone'].count()
    final['NumToneFullSpan'] = final['NumToneFullSpan'].fillna(0)
    final['MeanToneFullSpan'] = original[(original['language']=='es')&(original['taxonomy'].map(lambda d: len(d)) > 0)]\
    .groupby('date')['tone'].mean()
    final['StdToneFullSpan'] = original[(original['language']=='es')&(original['taxonomy'].map(lambda d: len(d)) > 0)]\
    .groupby('date')['tone'].std()
    
    final['NumToneFullEng'] = original[(original['language']=='en')&(original['taxonomy'].map(lambda d: len(d)) > 0)]\
    .groupby('date')['tone'].count()
    final['NumToneFullEng'] = final['NumToneFullEng'].fillna(0)
    final['MeanToneFullEng'] = original[(original['language']=='en')&(original['taxonomy'].map(lambda d: len(d)) > 0)]\
    .groupby('date')['tone'].mean()
    final['StdToneFullEng'] = original[(original['language']=='en')&(original['taxonomy'].map(lambda d: len(d)) > 0)]\
    .groupby('date')['tone'].std()
    
    #Tax
    CmpList = ['m1','m2','m3']    
    CtyList = ['m4','m5','m6']
    GovList = ['m7','m8','m9']
    
    #Cmp
    final['NumToneCmpLan'] = original[((original['language']=='en')|(original['language']=='es'))&(original['taxonomy'].apply(lambda x: sum([i[:2] in CmpList for i in x]) > 0))]\
    .groupby('date')['tone'].count()
    final['NumToneCmpLan'] = final['NumToneCmpLan'].fillna(0) 
    final['MeanToneCmpLan'] = original[((original['language']=='en')|(original['language']=='es'))&(original['taxonomy'].apply(lambda x: sum([i[:2] in CmpList for i in x]) > 0))]\
    .groupby('date')['tone'].mean()
    final['StdToneCmpLan'] = original[((original['language']=='en')|(original['language']=='es'))&(original['taxonomy'].apply(lambda x: sum([i[:2] in CmpList for i in x]) > 0))]\
    .groupby('date')['tone'].std()
    
    final['NumToneCmpSpan'] = original[(original['language']=='es')&(original['taxonomy'].apply(lambda x: sum([i[:2] in CmpList for i in x]) > 0))]\
    .groupby('date')['tone'].count()
    final['NumToneCmpSpan'] = final['NumToneCmpSpan'].fillna(0) 
    final['MeanToneCmpSpan'] = original[(original['language']=='es')&(original['taxonomy'].apply(lambda x: sum([i[:2] in CmpList for i in x]) > 0))]\
    .groupby('date')['tone'].mean()
    final['StdToneCmpSpan'] = original[(original['language']=='es')&(original['taxonomy'].apply(lambda x: sum([i[:2] in CmpList for i in x]) > 0))]\
    .groupby('date')['tone'].std()
    
    final['NumToneCmpEng'] = original[(original['language']=='en')&(original['taxonomy'].apply(lambda x: sum([i[:2] in CmpList for i in x]) > 0))]\
    .groupby('date')['tone'].count()
    final['NumToneCmpEng'] = final['NumToneCmpEng'].fillna(0)
    final['MeanToneCmpEng'] = original[(original['language']=='en')&(original['taxonomy'].apply(lambda x: sum([i[:2] in CmpList for i in x]) > 0))]\
    .groupby('date')['tone'].mean()
    final['StdToneCmpEng'] = original[(original['language']=='en')&(original['taxonomy'].apply(lambda x: sum([i[:2] in CmpList for i in x]) > 0))]\
    .groupby('date')['tone'].std()
    
    #CtyList
    final['NumToneCtyLan'] = original[((original['language']=='en')|(original['language']=='es'))&(original['taxonomy'].apply(lambda x: sum([i[:2] in CtyList for i in x]) > 0))]\
    .groupby('date')['tone'].count()
    final['NumToneCtyLan'] = final['NumToneCtyLan'].fillna(0)
    final['MeanToneCtyLan'] = original[((original['language']=='en')|(original['language']=='es'))&(original['taxonomy'].apply(lambda x: sum([i[:2] in CtyList for i in x]) > 0))]\
    .groupby('date')['tone'].mean()
    final['StdToneCtyLan'] = original[((original['language']=='en')|(original['language']=='es'))&(original['taxonomy'].apply(lambda x: sum([i[:2] in CtyList for i in x]) > 0))]\
    .groupby('date')['tone'].std()
    
    final['NumToneCtySpan'] = original[(original['language']=='es')&(original['taxonomy'].apply(lambda x: sum([i[:2] in CtyList for i in x]) > 0))]\
    .groupby('date')['tone'].count()
    final['NumToneCtySpan'] = final['NumToneCtySpan'].fillna(0)
    final['MeanToneCtySpan'] = original[(original['language']=='es')&(original['taxonomy'].apply(lambda x: sum([i[:2] in CtyList for i in x]) > 0))]\
    .groupby('date')['tone'].mean()
    final['StdToneCtySpan'] = original[(original['language']=='es')&(original['taxonomy'].apply(lambda x: sum([i[:2] in CtyList for i in x]) > 0))]\
    .groupby('date')['tone'].std()
    
    final['NumToneCtyEng'] = original[(original['language']=='en')&(original['taxonomy'].apply(lambda x: sum([i[:2] in CtyList for i in x]) > 0))]\
    .groupby('date')['tone'].count()
    final['NumToneCtyEng'] = final['NumToneCtyEng'].fillna(0)
    final['MeanToneCtyEng'] = original[(original['language']=='en')&(original['taxonomy'].apply(lambda x: sum([i[:2] in CtyList for i in x]) > 0))]\
    .groupby('date')['tone'].mean()
    final['StdToneCtyEng'] = original[(original['language']=='en')&(original['taxonomy'].apply(lambda x: sum([i[:2] in CtyList for i in x]) > 0))]\
    .groupby('date')['tone'].std()
    
    #GovList
    final['NumToneGovLan'] = original[((original['language']=='en')|(original['language']=='es'))&(original['taxonomy'].apply(lambda x: sum([i[:2] in GovList for i in x]) > 0))]\
    .groupby('date')['tone'].count()
    final['NumToneGovLan'] = final['NumToneGovLan'].fillna(0)
    final['MeanToneGovLan'] = original[((original['language']=='en')|(original['language']=='es'))&(original['taxonomy'].apply(lambda x: sum([i[:2] in GovList for i in x]) > 0))]\
    .groupby('date')['tone'].mean()
    final['StdToneGovLan'] = original[((original['language']=='en')|(original['language']=='es'))&(original['taxonomy'].apply(lambda x: sum([i[:2] in GovList for i in x]) > 0))]\
    .groupby('date')['tone'].std()
    
    final['NumToneGovSpan'] = original[(original['language']=='es')&(original['taxonomy'].apply(lambda x: sum([i[:2] in GovList for i in x]) > 0))]\
    .groupby('date')['tone'].count()
    final['NumToneGovSpan'] = final['NumToneGovSpan'].fillna(0)
    final['MeanToneGovSpan'] = original[(original['language']=='es')&(original['taxonomy'].apply(lambda x: sum([i[:2] in GovList for i in x]) > 0))]\
    .groupby('date')['tone'].mean()
    final['StdToneGovSpan'] = original[(original['language']=='es')&(original['taxonomy'].apply(lambda x: sum([i[:2] in GovList for i in x]) > 0))]\
    .groupby('date')['tone'].std()
    
    final['NumToneGovEng'] = original[(original['language']=='en')&(original['taxonomy'].apply(lambda x: sum([i[:2] in GovList for i in x]) > 0))]\
    .groupby('date')['tone'].count()
    final['NumToneGovEng'] = final['NumToneGovEng'].fillna(0)
    final['MeanToneGovEng'] = original[(original['language']=='en')&(original['taxonomy'].apply(lambda x: sum([i[:2] in GovList for i in x]) > 0))]\
    .groupby('date')['tone'].mean()
    final['StdToneGovEng'] = original[(original['language']=='en')&(original['taxonomy'].apply(lambda x: sum([i[:2] in GovList for i in x]) > 0))]\
    .groupby('date')['tone'].std()
    
    return(final)
    
    