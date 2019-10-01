# NLP-POLITICAL-RISK

This is the repository of NLP Political Risk project. Here is the instruction and documentation of the whole project. 

## Part 1: Query

* First,sign up a google cloud account and actived, search 'BigQuery Data Transfer API' in the console, then click 'ENABLE'.

<p align="center">
  <img src="https://github.com/globalaiorg/NLP-POLITICAL-RISK/blob/master/image/image1.jpg">
</p>

* Click this link https://bigquery.cloud.google.com/table/gdelt-bq:full.events?pli=1 and get into the database.

* After get into the webpage, find the database __events_partitioned__ under the gdelt-bq:gdeltv2.

* On the left of the webpage, click the downward arrow sign on __My First Project__, click on __Create new dataset__(If you didn’t have one before), and give a name of __Dataset ID__, then click __OK__.

* Click the __Query Table__ on the upper right, then write the code and click __Run Query__ to query the dataset. 
  
  For instance, if we want to query the the data from Argentina, the code is following,
```
SELECT * FROM [gdelt-bq:gdeltv2.events_partitioned]
#WHERE _PARTITIONTIME >= "2015-03-01 00:00:00" AND _PARTITIONTIME < "2016-04-01 00:00:00"
where (MonthYear>=201503 and MonthYear<201604)
and (Actor1CountryCode like "ARG" or Actor1Geo_CountryCode like "AR"
or Actor1Geo_FullName like "%Argentina%" or Actor2Geo_FullName like "%Argentina%"
or Actor2CountryCode like "ARG" or Actor2Geo_CountryCode like "AR"
or Actor1Code like "ARG" or Actor1Name like "ARGENTINA"
or Actor2Code like "ARG" or Actor2Name like "ARGENTINA"
or ActionGeo_FullName like "%Argentina%" or ActionGeo_CountryCode like"AR")
```
Note: There are some country may use abbreviation and other extension like 'Argentina Government', so we need to use SQL grammar 'like' when query the dataset.

* When finished query the code, click __Save as Table__ on the right side. The window shows like this: 

<p align="center">
  <img src="https://github.com/globalaiorg/NLP-POLITICAL-RISK/blob/master/image/Screen%20Shot%202019-07-30%20at%2010.52.58.png">
</p>

* Click 'View Files' and follow the instruction to create a new bucket(if didn’t have one before), and write the URL like the example in the picture: 'bucketname/foldername(if has)/datafilename'. e.g.: Mybucket/Argentina/201501.csv

<p align="center">
  <img src="https://github.com/globalaiorg/NLP-POLITICAL-RISK/blob/master/image/image2.png">
</p>

* The file is saved on the Google Cloud Platform, then download them on local computer.

## Part 2: Downloading and Cleaning

* If there are lots of lines in the datafile we should seperate them by month and saved as 'csv' file(also we can say by column ‘MonthYear’) in order to use multiprocessing step later. Use template code __Sort_by_Month.ipynb__

* Load the csv datafile and save them into pickle file. Use template code __pickle_cleaning.ipynb__ or __code_for_mp.ipynb__. Remember to change the list ‘Date_file’,the target, and args if needed. 
  Note: Remember to save the files and code into same directory.

* Use template code __text_downloading.ipynb__ to get the language list, then count number and percentage of each unique language. 

* Based on the percentage, choose top 2 or 3 language to translate.

* Download all the text of the news and set the language of the text by using the template code __text_downloading.py__

* Mapping with English triggerlist (this part would be done on the big computer, don’t need to do it on your local computer).

Note: We sort and split the dataset by 'MonthYear' first in order to use multiprocessing later,  and then remove the duplicate URL. Then do the text downloading. In the meanwhile, detect the data size and language percentages of the events. 
And mapping the text with English trigger list. First, use triggerlist to get the taxonomy of each news(use function’read_trigger_config’ and ‘filter_stories_bypickle’ in events_pickle8.py). Then save the news list as a new pickle file. Second, count the daily avgtone, numnews, std using countNumAndMean_new1.ipynb and countStdAndCv_new1.ipynb, output as a csv file, the head format of the result is like this: 


The algorithm of each line is in the ipynb file.
The name rule is as follows:
Date, TotalNum
All, Full taxonomy and their tone, News in different languages, full taxonomy and their tone. Like:






## Part 3: Translate the Triggerlist

* Translate the English trigger list into the other languages: translate the part after ‘AND+’ or ‘TEXT+’, word by word, phrase by phrase, because this is a dictionary not article. For each word or phrase find the most frequency translation using google translate:https://translate.google.com keep all of the translation of which has a frequency level 3 or 2, the frequency shows as marked below:

<p align="center">
  <img src="https://github.com/globalaiorg/NLP-POLITICAL-RISK/blob/master/image/Screen%20Shot%202019-07-30%20at%2011.02.50.png">
</p>


Do the permutation and combination, create the new dictionary(the format is dictionary) and copy the translation into the
‘triggerlist_construction_translated.ipynb’, using ‘#’ to comment lines don’t delete it, because they will be used in the next part.

* Choose several dates with the most mapping frequency of English(the day with the biggest result of the column ‘NumNewsFullLan’ in Step2-4), mapping these days' news with the language triggerlist we translated, get the taxonomy of the news of the language we translate.

* Coordinate translated triggerlist with the values frequency we get: Keep the translations have mapped, or keep all if none of them are mapped.

## Part 4: Mapping Triggerlist With the Text 

* Mapping with the coordinated triggerlist we got in Step3, using the code in Step2, get the __csv__ file we want.

## Part 5: Visualization

* 1.Use the temple code __result_combination.ipynb__ to convert the daily result into weekly(7 days moving average), and then convert them into Tableau format by using the code __convert_Tableau.ipynb__ .

* Visualized them by Tableau.

* Get the wordcloud by each peak day by using the template code __wc, bigrams,trigrams_Final.ipynb__ . 

Note: The way to find peak day is count the column 'AvgToneFullLan'.


## Part 6: Forcasting

* Using model to predict the future's tone.








