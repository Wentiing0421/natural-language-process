#!/usr/bin/env python
# coding: utf-8

# In[16]:


import pandas as pd
import multiprocessing as mp
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
from time import ctime
from langdetect import detect
import threading

def process(df, *args): #input filename
    """
    Fetches news items from export.csv file
    Returns a list of News.
    """
#        try:
#            pubdate = datetime.strptime(pubdate, "%a, %d %b %Y %H:%M:%S %Z")
#            pubdate.replace(tzinfo=pytz.timezone("GMT"))
#          #  pubdate = pubdate.astimezone(pytz.timezone('EST'))
#          #  pubdate.replace(tzinfo=None)
#        except ValueError:
#            pubdate = datetime.strptime(pubdate, "%a, %d %b %Y %H:%M:%S %z")

#    df = pd.read_csv('20131126.csv')
    ret = []
    for index,row in df.iterrows():
        country_Code = row['Actor1CountryCode']
        sqldate = row['SQLDATE']
        month_year = row['MonthYear']
        tone = row['AvgTone']
        url = row['SOURCEURL']
        news = News(country_Code,sqldate,month_year,tone,url)
        ret.append(news)
    print('\nThere are %d items in News.'% len(ret))
    return ret

class News:
    def __init__(self,countryCode,sqldate,month_year,tone,url):
        self.countryCode = countryCode
        self.sqldate = sqldate
        self.month_year = month_year
        self.tone = tone
        self.url = url
        self.text = None
        self.publish_date = None
        self.taxonomy = []
        self.language = []

    def get_sqldate(self):
        return self.sqldate
    def get_countryCode(self):
        return self.countryCode
    def get_tone(self):
        return self.tone
    def get_monthyear(self):
        return self.month_year
    def get_url(self):
        return self.url
    def get_text(self):
        return self.text
    def get_publish_date(self):
        return self.publish_date
    def get_taxonomy(self):
        return self.taxonomy
    def set_taxonomy(self,taxonomy):
        self.taxonomy.append(taxonomy)
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
            print('Success.')
        except:
            self.text,self.publish_date = None, None
            print('No text found.')

class Trigger:
    def evaluate(self, story):
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
    def evaluate(self, story):
        return self.is_phrase_in(story)
    
    def is_phrase_in(self, text):
        raw_text = text.lower()
        raw_phrase = self.phrase.lower()
        #print('mapping is_phrase_in')
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
    def evaluate(self, story):
        #print('evaluate')
        return self.is_phrase_in(story.get_text())

class AndTrigger(Trigger):
    def __init__(self, *args):
        self.args = args
        
    def get_args(self):
        phrase_list = [arg.get_phrase() for arg in self.args]
        return '+'.join(phrase_list)
    def evaluate(self, story):
        #print('evaluate')
        true_list = [T.evaluate(story) for T in self.args]
        result = (True, False)[False in true_list]
        return result
#        return self.T1.evaluate(story) and self.T2.evaluate(story) and self.T3.evaluate(story)

class OrTrigger(Trigger):
    def __init__(self,*args):
        self.args = args
    def get_args(self):
        phrase_list = [arg.get_phrase() for arg in self.args]
        return '+'.join(phrase_list)
    def evaluate(self, story):
        true_list = [T.evaluate(story) for T in self.args]
        result = (False,True)[True in true_list]
        return result
    
class NotTrigger(Trigger):
    def __init__(self, T):
        self.T = T
    def get_T(self):
        return self.T
    def evaluate(self, story):
        return not self.T.evaluate(story)

    
def read_trigger_config(filename):
    """
    filename: the name of a trigger configuration file

    Returns: a list of trigger objects specified by the trigger configuration
        file.
    """
    #print('start reading trig')
    trigger_file = open(filename, 'r', encoding='utf-8')
    lines = []
    for line in trigger_file:
        line = line.rstrip()
        if not (len(line) == 0 or line.startswith('//')):
            lines.append(line)
    
    # TODO: Problem 11
    # line is the list of lines that you need to parse and for which you need
    # to build triggers
#    trigger_list = []
    trigger_dict = {}
    
    for line in lines:
        l_item = line.split('+')
        #print(l_item)
        #print(len(l_item))
#        if l_item[0] == 'ADD':
#            for item in l_item[1:]:
#                trigger_list.append(trigger_dict[item])
        if l_item[1] == 'TEXT':
            trigger_dict[l_item[0]] = TextTrigger(l_item[2])
        elif l_item[1] == 'AND':
            arg_tuple = tuple(TextTrigger(item) for item in l_item[2:])
            trigger_dict[l_item[0]] = AndTrigger(*arg_tuple)
        
#            if l_item[1] == 'TITLE':
#                trigger_dict[l_item[0]] = TitleTrigger(l_item[2])    
#            elif l_item[1] == 'DESCRIPTION':
#                trigger_dict[l_item[0]] = DescriptionTrigger(l_item[2])
#            elif l_item[1] == 'AFTER':
#                trigger_dict[l_item[0]] = AfterTrigger(l_item[2])
#            elif l_item[1] == 'BEFORE':
#                trigger_dict[l_item[0]] = BeforeTrigger(l_item[2])
#            elif l_item[1] == 'NOT':
#                T_not = trigger_dict[l_item[2]]
#                trigger_dict[l_item[0]] = NotTrigger(T_not)
#            elif l_item[1] == 'AND':
#                T_and1 = trigger_dict[l_item[2]]
#                T_and2 = trigger_dict[l_item[3]]
#                trigger_dict[l_item[0]] = AndTrigger(T_and1,T_and2)
#            elif l_item[1] == 'OR':
#                T_or1 = trigger_dict[l_item[2]]
#                T_or2 = trigger_dict[l_item[3]]
#                trigger_dict[l_item[0]] = OrTrigger(T_or1,T_or2)
    
    print(lines) # for now, print it so you see what it contains!
    return trigger_dict    
    
def filter_stories(stories,trigger_dict_eng,trigger_dict_span,num_line):
    """
    Takes in a list of News instances.

    Returns: a list of only the stories for which a trigger in triggerlist fires.
    """
#    trig_story = []
    temp_stories = stories[:num_line]
    for index, story in enumerate(temp_stories):
        print('\n'+str(index),end=' ')
        #print(story.get_gevent_id(),story.get_dateAdded())
        story.clean_text()
        if story.get_text() == None:
            pass
        else:
            try:
                detect(story.text)
                if detect(story.text) == 'en':
                    story.set_language('en')
                    #print(type(story.get_language()))
                    print(story.get_language())
                    for key,trig in trigger_dict_eng.items():
                        try:
                            story.set_taxonomy((key,trig.get_args())) if trig.evaluate(story)                         else ctime()#print('False',end=' ')
                        except AttributeError:
                            pass
                if detect(story.text) == 'es':
                    story.set_language('es')
                    #print(type(story.get_language()))
                    print(story.get_language()) 
                    for key,trig in trigger_dict_span.items():
                        try:
                            story.set_taxonomy((key,trig.get_args())) if trig.evaluate(story)                         else ctime()#print('False',end=' ')
                        except AttributeError:
                            pass
            except:
                print('error')
        print(story.get_taxonomy())

def filter_stories_bypickle(feng,trigger_dict_eng,trigger_dict_span,num_line):
    """
    Takes in a list of News instances which placing in pickle.

    Returns: a list of only the stories for which a trigger in triggerlist fires.
    """
#    trig_story = []
    temp_stories = feng[:num_line]
    for index, story in enumerate(temp_stories):
    #for index in range(num_line):
        print(index)
        if story.get_language() != []:
            if story.get_language()[0] == 'en':
                #print('mapping eng')
                for key,trig in trigger_dict_eng.items():
                    try:
                        #print('mapping step 2 eng')
                        story.set_taxonomy((key,trig.get_args())) if trig.evaluate(story)                     else ctime()#print('False',end=' ')
                    except AttributeError:
                        pass
            if story.get_language()[0] == 'es':
                #print('mapping span')
                for key,trig in trigger_dict_span.items():
                    try:
                        #print('mapping step 2 span')
                        story.set_taxonomy((key,trig.get_args())) if trig.evaluate(story)                     else ctime()#print('False',end=' ')
                    except AttributeError:
                        pass
        print(story.get_taxonomy())
        
def FilterCountry(ActorCountiesList,f):
    news_list = []
    if len(ActorCountiesList)==1:
        news_list.extend(process(pd.read_csv(f),ActorCountiesList))#filter the news by country
    elif len(ActorCountiesList) > 1:
        news_list.extend(process(pd.read_csv(f),*ActorCountiesList))
    else:
        print('No ActorCounties has been given')
    return news_list
def Mappingdict(DateFile,MappingLanguageList,news_list,Csv):
    #NumNews = [0 for i in range(len(TriggerList))]
    TriggerList = MappingLanguageList
    #BOPRList = ['s1','s2','s3','s4','m1','m2']
    #GCTCList = ['m3','m4','m5','m6','m7','m8','m9','m10','m11','m12','m13','m14','m15','m16','m17','m18','m19','m20','m21','m22','m23','m24']
    #GISOList = ['m25','m26','m27','m28','m29','m30','m31','m32','m33','m34','m35','m36','m37','m38','m39','m40','m41']
    CmpList = ['m1','m2','m3']
    CtyList = ['m4','m5','m6']
    if len(TriggerList)==0:
        print('No TriggerList has been given')
    else:
        print('Start Mapping')
        nn = 0
        trig_dict_eng = read_trigger_config(TriggerList[0])
        trig_dict_span = read_trigger_config(TriggerList[1])
        num_line = len(news_list)
        news_list_private = news_list
        filter_stories(news_list_private,trig_dict_eng,trig_dict_span,num_line)
        fsplit = 'arg'+DateFile.split('.')[0]+'cty.p'
        pickle.dump(news_list_private, open(fsplit,'wb'))
        with open(fsplit,'rb') as PickleFiles:
            feng = pickle.loads(PickleFiles.read())
        NumNewsAll = 0
        TotalToneAll = 0
        TotalToneAllEng = 0
        TotalToneCmpEng = 0
        TotalToneCtyEng = 0
        NumNewsAllEng = 0
        NumNewsCmpEng = 0
        NumNewsCtyEng = 0
        TotalToneAllSpan = 0
        TotalToneCmpSpan = 0
        TotalToneCtySpan = 0
        TotalToneGISOSpan = 0
        NumNewsAllSpan = 0
        NumNewsCmpSpan = 0
        NumNewsCtySpan = 0
        NumNewsGISOSpan = 0
        for i in range(num_line):
            #print(feng[i].get_text())
            TotalToneAll += feng[i].get_tone()
            NumNewsAll += 1
            #print(news_list[i].get_language())
            #f.split('/')[-1].split('.')[0]
            #taxo = news_list[i].get_taxonomy()[0][0]
            if feng[i].get_language() != []:
                print(feng[i].get_language())
                if feng[i].get_language()[0] == 'en':
                    print(feng[i].get_language()[0])
                    TotalToneAllEng += feng[i].get_tone()
                    NumNewsAllEng += 1
                    if feng[i].get_taxonomy() !=[]:
                        taxo = feng[i].get_taxonomy()[-1][0][0:2]
                        print(feng[i].get_taxonomy())
                        if taxo in CmpList:
                            TotalToneCmpEng += feng[i].get_tone()
                            NumNewsCmpEng += 1
                        if taxo in CtyList:
                            TotalToneCtyEng += feng[i].get_tone()
                            NumNewsCtyEng += 1
                        
                if feng[i].get_language()[0] == 'es':
                    print(feng[i].get_language()[0])
                    TotalToneAllSpan += feng[i].get_tone()
                    NumNewsAllSpan += 1
                    if feng[i].get_taxonomy() !=[]:
                        taxo = feng[i].get_taxonomy()[-1][0][0:2]
                        print(feng[i].get_taxonomy())
                        if taxo in CmpList:
                            TotalToneCmpSpan += feng[i].get_tone()
                            NumNewsCmpSpan += 1
                        if taxo in CtyList:
                            TotalToneCtySpan += feng[i].get_tone()
                            NumNewsCtySpan += 1
                        
                        
            if i < num_line - 1:
                if feng[i].get_sqldate() != feng[i+1].get_sqldate():
                    #print(news_list[i].get_sqldate())
                    Csv[nn][0] = feng[i].get_sqldate()
                    Csv[nn][1] = TotalToneAll
                    Csv[nn][2] = NumNewsAll
                    if NumNewsAll != 0:
                        Csv[nn][3] = TotalToneAll/NumNewsAll
                    Csv[nn][4] = TotalToneAllEng
                    Csv[nn][5] = NumNewsAllEng
                    if NumNewsAllEng != 0:
                        Csv[nn][6]  = TotalToneAllEng/NumNewsAllEng
                    Csv[nn][7] = TotalToneCmpEng
                    Csv[nn][8] = NumNewsCmpEng
                    if NumNewsCmpEng != 0:
                        Csv[nn][9]  = TotalToneCmpEng/NumNewsCmpEng
                    Csv[nn][10] = TotalToneAllSpan
                    Csv[nn][11] = NumNewsAllSpan
                    if NumNewsAllSpan != 0:
                        Csv[nn][12]  = TotalToneAllSpan/NumNewsAllSpan
                    Csv[nn][13] = TotalToneCmpSpan
                    Csv[nn][14] = NumNewsCmpSpan
                    if NumNewsCmpSpan != 0:
                        Csv[nn][15]  = TotalToneCmpSpan/NumNewsCmpSpan
                    NumNewsAll = 0
                    TotalToneAll = 0
                    TotalToneAllEng = 0
                    TotalToneCmpEng = 0
                    TotalToneCtyEng = 0
                    TotalToneGISOEng = 0
                    NumNewsAllEng = 0
                    NumNewsCmpEng = 0
                    NumNewsCtyEng = 0
                    NumNewsGISOEng = 0
                    TotalToneAllSpan = 0
                    TotalToneCmpSpan = 0
                    TotalToneCtySpan = 0
                    TotalToneGISOSpan = 0
                    NumNewsAllSpan = 0
                    NumNewsCmpSpan = 0
                    NumNewsCtySpan = 0
                    NumNewsGISOSpan = 0
                    nn += 1
                    #print(nn)
                    #print(ctime())
            if i == num_line - 1:
                Csv[nn][0] = feng[i].get_sqldate()
                Csv[nn][1] = TotalToneAll
                Csv[nn][2] = NumNewsAll
                if NumNewsAll != 0:
                    Csv[nn][3] = TotalToneAll/NumNewsAll
                Csv[nn][4] = TotalToneAllEng
                Csv[nn][5] = NumNewsAllEng
                if NumNewsAllEng != 0:
                    Csv[nn][6]  = TotalToneAllEng/NumNewsAllEng
                Csv[nn][7] = TotalToneCmpEng
                Csv[nn][8] = NumNewsCmpEng
                if NumNewsCmpEng != 0:
                    Csv[nn][9]  = TotalToneCmpEng/NumNewsCmpEng
                Csv[nn][10] = TotalToneAllSpan
                Csv[nn][11] = NumNewsAllSpan
                if NumNewsAllSpan != 0:
                    Csv[nn][12]  = TotalToneAllSpan/NumNewsAllSpan
                Csv[nn][13] = TotalToneCmpSpan
                Csv[nn][14] = NumNewsCmpSpan
                if NumNewsCmpSpan != 0:
                    Csv[nn][15]  = TotalToneCmpSpan/NumNewsCmpSpan
    return Csv
              
def WritetoCsv(DateFile,Csv):
    resultfile = 'resultfile'+DateFile.split('.')[0]+'cty.csv'
    with open(resultfile,'w', newline = '') as InputF:
        csv_write = csv.writer(InputF)
        csv_head1 = ['Date','TotalToneAll','NumNewsAll','AvgToneAll',
                     'TotalToneAllEng','NumNewsAllEng','AvgToneAllEng',
                     'TotalToneGovEng','NumNewsGovEng','AvgToneGovEng',
                     'TotalToneAllSpan','NumNewsAllSpan','AvgToneAllSpan',
                     'TotalToneGovSpan','NumNewsGovSpan','AvgToneGovSpan',]
        csv_write.writerow(csv_head1)
        csv_write.writerows(Csv)
    print('writing finished')

def events_tonestatistic(DateFile, ActorCountiesList, MappingLanguageList):
    """
    
    """
    #fileName = ['20150820.csv','20150830.csv','20150914.csv','20151009.csv','20151125.csv','20151221.csv']
    #ActorCountiesList = ['ARG','Covering']
    #MappingLanguageList = ['triggerlist-english-co.txt','triggerlist-Spanish-extend-f.txt']
    #DateFile = 
    news_list = FilterCountry(ActorCountiesList,DateFile)
    Csv = [[0 for i in range(13)] for i in range(31)]
    print(ctime())
    Mappingdict(DateFile,MappingLanguageList,news_list,Csv)#mapping the news with the dictionary
    print(ctime())
    WritetoCsv(DateFile,Csv)


# In[ ]:




