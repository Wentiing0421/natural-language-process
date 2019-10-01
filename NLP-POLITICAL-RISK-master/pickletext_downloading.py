#!/usr/bin/env python
# coding: utf-8

# In[2]:


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

def pickletext_downloading(picklefilename,rename):
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
    pickle.dump(news_list, open(rename,'wb'))
    return language_list


# In[3]:


language_list = pickletext_downloading('arg20150830eng.p','arg20150830.p')


# In[ ]:




