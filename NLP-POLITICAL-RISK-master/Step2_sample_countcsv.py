#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Aug 21 15:00:46 2019

@author: zhoushuyi
"""

import numpy as np
import pickle
#from AddColumns import *
from part1to4 import*
import pandas as pd

class News:
    def __init__(self, sqldate, month_year, goldstein_scale, num_mentions, num_sources, num_articles, tone, url):
        self.sqldate = sqldate
        self.month_year = month_year
        #self.event_root_code = event_root_code
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

################ ################ ################ ################ clmcode

url,sqldate,goldstein_scale,num_mentions,num_articles,tone,taxonomy,language,text = \
[],[],[],[],[],[],[],[],[]
    
#with open('new201507.p','rb') as PickleFiles:
with open('new2015072500.p','rb') as PickleFiles:    
    news_list = pickle.loads(PickleFiles.read())
    for story in news_list:
        url.append(story.url)
        sqldate.append(story.sqldate)
        goldstein_scale.append(story.goldstein_scale)
        num_mentions.append(story.num_mentions)
        num_articles.append(story.num_articles)
        tone.append(story.tone)
        taxonomy.append(story.taxonomy)
        language.append(story.language)
        text.append(story.get_text())
        
original=pd.DataFrame({"URL":url, 
                        "date":sqldate, 
                        "goldstein_scale":goldstein_scale, 
                        "num_mentions":num_mentions, 
                        "num_articles":num_articles, 
                         "tone":tone, 
                         "taxonomy":taxonomy, 
                         "language":language,
                         "text":text})     

pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)
original.head()
    
    
################ ################ ################ ################   


final=pd.DataFrame()
original['language'] = original['language'].apply(lambda x:x[0])

final['NumUniqueUrl'] = original.groupby('date')['URL'].apply(lambda x: x.unique().shape[0])
final['NumUniqueUrlwithArticle'] = original.groupby('date')['text'].apply(lambda x: x.notnull().count())
final['MeanToneAllAll'] = original.groupby('date')['tone'].mean()
final['StdToneAllAll'] = original.groupby('date')['tone'].std()

final['NumToneAllSpan'] = original.groupby('date')['language'].apply(lambda x: sum(x=='es'))# if language=[es]
final['MeanToneAllSpan'] =original[original['language']=='es'].groupby('date')['tone'].mean()
final['StdToneAllSpan'] = original[original['language']=='es'].groupby('date')['tone'].std()

final['NumToneAllEng'] = original.groupby('date')['language'].apply(lambda x: sum(x=='en'))
final['MeanToneAllEng'] = original[original['language']=='en'].groupby('date')['tone'].mean()
final['StdToneAllEng'] = original[original['language']=='en'].groupby('date')['tone'].std()

#full:taxonomy!=[] 
final['NumToneFullLan'] = final['NumToneFullSpan']+final['NumToneFullEng']
final['MeanToneFullLan'] = final['MeanToneFullEng']+final['MeanToneFullSpan']
final['StdToneFullLan'] = df1+df2
final['StdToneFullLan']=final['StdToneFullLan'].replace(0,np.NaN)

final['NumToneFullEng'] = original[(original['language']=='en')&(original['taxonomy'].map(lambda d: )]\
.groupby('date')['tone'].count()
final['NumToneFullEng']=final['NumToneFullEng'].fillna(0)
final['MeanToneFullEng'] = original[(original['language']=='en')&(original['taxonomy'].map(lambda d: len(d)) > 0)]\
.groupby('date')['tone'].mean()
final['MeanToneFullEng']=final['MeanToneFullEng'].fillna(0)
final['StdToneFullEng'] = original[(original['language']=='en')&(original['taxonomy'].map(lambda d: len(d)) > 0)]\
.groupby('date')['tone'].std()
df1=final['StdToneFullEng'].fillna(0)

final['NumToneFullSpan'] = original[(original['language']=='es')&(original['taxonomy'].map(lambda d: len(d)) > 0)]\
.groupby('date')['tone'].count()
final['NumToneFullSpan']=final['NumToneFullSpan'].fillna(0)
final['MeanToneFullSpan'] = original[(original['language']=='es')&(original['taxonomy'].map(lambda d: len(d)) > 0)]\
.groupby('date')['tone'].mean()
final['MeanToneFullSpan']=final['MeanToneFullSpan'].fillna(0)
final['StdToneFullSpan'] = original[(original['language']=='es')&(original['taxonomy'].map(lambda d: len(d)) > 0)]\
.groupby('date')['tone'].std()
df2=final['StdToneFullSpan'].fillna(0)

#Cmp
CmpList = ['m1','m2','m3']    
CtyList = ['m4','m5','m6']
GovList = ['m7','m8','m9']


final['NumToneCmpLan'] = final['NumToneCmpSpan']+final['NumToneCmpEng']
final['MeanToneCmpLan'] = df5+df6
final['MeanToneCmpLan']=final['MeanToneCmpLan'].replace(0,np.NaN)
final['StdToneCmpLan'] = df1+df2
final['StdToneCmpLan']=final['StdToneCmpLan'].replace(0,np.NaN)

final['NumToneCmpEng'] = original[(original['language']=='en')&(original['taxonomy'].apply(lambda x: sum([i[:2] in CmpList for i in x]) > 0))]\
.groupby('date')['tone'].count()
final['NumToneCmpEng']=final['NumToneCmpEng'].fillna(0)
final['MeanToneCmpEng'] = original[(original['language']=='en')&(original['taxonomy'].apply(lambda x: sum([i[:2] in CmpList for i in x]) > 0))]\
.groupby('date')['tone'].mean()
df5=final['MeanToneCmpEng'].fillna(0)
final['StdToneCmpEng'] = original[(original['language']=='en')&(original['taxonomy'].apply(lambda x: sum([i[:2] in CmpList for i in x]) > 0))]\
.groupby('date')['tone'].std()
df3=final['StdToneCmpEng'].fillna(0)

final['NumToneCmpSpan'] = original[(original['language']=='es')&(original['taxonomy'].apply(lambda x: sum([i[:2] in CmpList for i in x]) > 0))]\
.groupby('date')['tone'].count()
final['NumToneCmpSpan']=final['NumToneCmpSpan'].fillna(0)
final['MeanToneCmpSpan'] = original[(original['language']=='es')&(original['taxonomy'].apply(lambda x: sum([i[:2] in CmpList for i in x]) > 0))]\
.groupby('date')['tone'].mean()
df6=final['MeanToneCmpSpan'].fillna(0)
final['StdToneCmpSpan'] = original[(original['language']=='es')&(original['taxonomy'].apply(lambda x: sum([i[:2] in CmpList for i in x]) > 0))]\
.groupby('date')['tone'].std()
df4=final['StdToneCmpEng'].fillna(0)

#Cty
final['NumToneCtyLan'] = final['NumToneCtySpan']+final['NumToneCtyEng']
final['MeanToneCtyLan'] = df5+df6
final['MeanToneCtyLan']=final['MeanToneCtyLan'].replace(0,np.NaN)
final['StdToneCtyLan'] = df1+df2
final['StdToneCtyLan']=final['StdToneCtyLan'].replace(0,np.NaN)

final['NumToneCtyEng'] = original[(original['language']=='en')&(original['taxonomy'].apply(lambda x: sum([i[:2] in CtyList for i in x]) > 0))]\
.groupby('date')['tone'].count()
final['NumToneCtyEng']=final['NumToneCtyEng'].fillna(0)
final['MeanToneCtyEng'] = original[(original['language']=='en')&(original['taxonomy'].apply(lambda x: sum([i[:2] in CtyList for i in x]) > 0))]\
.groupby('date')['tone'].mean()
df5=final['MeanToneCtyEng'].fillna(0)
final['StdToneCtyEng'] = original[(original['language']=='en')&(original['taxonomy'].apply(lambda x: sum([i[:2] in CtyList for i in x]) > 0))]\
.groupby('date')['tone'].std()
df3=final['StdToneCtyEng'].fillna(0)

final['NumToneCtySpan'] = original[(original['language']=='es')&(original['taxonomy'].apply(lambda x: sum([i[:2] in CtyList for i in x]) > 0))]\
.groupby('date')['tone'].count()
final['NumToneCtySpan']=final['NumToneCtySpan'].fillna(0)
final['MeanToneCtySpan'] = original[(original['language']=='es')&(original['taxonomy'].apply(lambda x: sum([i[:2] in CtyList for i in x]) > 0))]\
.groupby('date')['tone'].mean()
df6=final['MeanToneCtySpan'].fillna(0)
final['StdToneCtySpan'] = original[(original['language']=='es')&(original['taxonomy'].apply(lambda x: sum([i[:2] in CtyList for i in x]) > 0))]\
.groupby('date')['tone'].std()
df4=final['StdToneCtyEng'].fillna(0)

#Gov
final['NumToneGovLan'] = final['NumToneGovSpan']+final['NumToneGovEng']
final['MeanToneGovLan'] = df5+df6
final['MeanToneGovLan']=final['MeanToneGovLan'].replace(0,np.NaN)
final['StdToneGovLan'] = df1+df2
final['StdToneGovLan']=final['StdToneGovLan'].replace(0,np.NaN)

final['NumToneGovEng'] = original[(original['language']=='en')&(original['taxonomy'].apply(lambda x: sum([i[:2] in GovList for i in x]) > 0))]\
.groupby('date')['tone'].count()
final['NumToneGovEng']=final['NumToneGovEng'].fillna(0)
final['MeanToneGovEng'] = original[(original['language']=='en')&(original['taxonomy'].apply(lambda x: sum([i[:2] in GovList for i in x]) > 0))]\
.groupby('date')['tone'].mean()
df5=final['MeanToneGovEng'].fillna(0)
final['StdToneGovEng'] = original[(original['language']=='en')&(original['taxonomy'].apply(lambda x: sum([i[:2] in GovList for i in x]) > 0))]\
.groupby('date')['tone'].std()
df3=final['StdToneGovEng'].fillna(0)

final['NumToneGovSpan'] = original[(original['language']=='es')&(original['taxonomy'].apply(lambda x: sum([i[:2] in GovList for i in x]) > 0))]\
.groupby('date')['tone'].count()
final['NumToneGovSpan']=final['NumToneGovSpan'].fillna(0)
final['MeanToneGovSpan'] = original[(original['language']=='es')&(original['taxonomy'].apply(lambda x: sum([i[:2] in GovList for i in x]) > 0))]\
.groupby('date')['tone'].mean()
df6=final['MeanToneGovSpan'].fillna(0)
final['StdToneGovSpan'] = original[(original['language']=='es')&(original['taxonomy'].apply(lambda x: sum([i[:2] in GovList for i in x]) > 0))]\
.groupby('date')['tone'].std()
df4=final['StdToneGovEng'].fillna(0)

final.to_csv('final.csv')
















##################################################################################
d['taxonomy'].apply(lambda x: sum([i[:2] in CmpList for i in x]) > 0)

sum([i[:2] in CmpList for i in x]) > 0


if -1:
    print(111)

sum([True])

sum([False])

int(True)

bool(2)










