#/bin/bash

hadoop fs -mkdir -p /user/ubuntu
hadoop fs -put lemmatization-it.txt
hadoop fs -put lexicon-it.csv
hadoop fs -put tweet_teams.csv
hadoop fs -put tweet_teams_sentiment.csv
hadoop fs -put tweet_players.csv
hadoop fs -put tweet_players_sentiment.csv

hadoop fs -ls
