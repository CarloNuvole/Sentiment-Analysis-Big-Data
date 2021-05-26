# ------------------------------------------------------------------------------
# Project: Sentiment Analysis for italian tweets using lexicon with Spark
#
# This .py is used to retrive real time tweets
#
# Input Parameters: <query_parameter> <number_tweets>
#  - <query_parameter>: use ' ' for multiple words (e.g. 'coppa italia')
#  - <number_tweets>: how many tweets to download
#
# Language used: Python
#
# Academic project (course: BIG DATA)
#
# (C) 2021 Carlo Nuvole & Luca Sedda, Università degli Studi di Cagliari, Italy
# Released under GNU Public License (GPL)
# ------------------------------------------------------------------------------

import sys
import csv
import tweepy
import datetime

consumer_key = ""
consumer_secret = ""
access_token = ""
access_token_secret = ""

if len(sys.argv) == 1:
    print("Errore: query non specificata")
    sys.exit()
else:
    query = sys.argv[1]

if len(sys.argv) == 2:
    nTweet = 10
    print("Numero di Tweet non specificato. Verranno scaricati " + str(nTweet) + " tweet")
else:
    nTweet = int(sys.argv[2])

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)

csvFile = open('tweet'+datetime.datetime.now().strftime("%d%b%Y")+'.csv', 'a')
csvWriter = csv.writer(csvFile)

print("Download di " + str(nTweet) + " tweet contenenti " + str(query) + " in corso...")

for tweet in tweepy.Cursor(api.search, lang="it",  q=query, tweet_mode="extended").items(nTweet):
    if not (hasattr(tweet, 'retweeted_status')):
        csvWriter.writerow([tweet.full_text.replace("\r", " ").replace("\n", " ").replace("\t", " ").replace("\\", " ").replace("\"","")])

    if (hasattr(tweet, 'retweeted_status')): # Per i retweet
        csvWriter.writerow([tweet.retweeted_status.full_text.replace("\r", " ").replace("\n", " ").replace("\t", " ").replace("\\", " ").replace("\"","")])