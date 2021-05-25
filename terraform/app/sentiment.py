# ------------------------------------------------------------------------------
# Project: Sentiment Analysis for italian tweets using lexicon with Spark
#
# Input Parameters: <number_slaves> <test> <path_tweet> <path_tweet_label>
#  - number_slaves: number of AWS datanodes
#  - test: 'True' to compare results with given labels, 'False' otherwise
#  - path_tweet: file path with tweets
#  - path_tweet_label: must be in a 'tsv' form. Necessary if <test> is 'True'
#
# Language used: Python
#
# Academic project (course: BIG DATA)
#
# (C) 2021 Carlo Nuvole & Luca Sedda, Università degli Studi di Cagliari, Italy
# Released under GNU Public License (GPL)
# ------------------------------------------------------------------------------

# LIBRARIES #

import re
import sys
import time
import pandas
import datetime

from pyspark.sql.functions import *
from pyspark.sql.types import *
from pyspark.sql import *

import nltk
nltk.download('popular')
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

# FUNCTIONS #

def compute_score(sentiment, score):

    if sentiment == 'negative':
        return -score

    return score

def compute_sentiment(score):

    if score < -0.35:
        return "NEGATIVE"
    elif score > 1.750:
        return "POSITIVE"

    return "NEUTRAL"

# GLOBAL VARIABLES #

NUMBER_PARTITIONS = int(sys.argv[1])
TEST_MODE = sys.argv[2].lower()
PATH_TWEET = sys.argv[3]

if TEST_MODE == 'true':
    PATH_TWEET_LABEL = sys.argv[4]

spark = SparkSession.builder.appName('PySpark - Sentiment Analysis').getOrCreate()
spark.sparkContext.setLogLevel('WARN')

path_lemm = 'lemmatization-it.txt'

schema_lemm = StructType([
    StructField("Lemma", StringType(), True),\
    StructField("Word", StringType(), True)])

lemm = spark.read.format('csv')\
    .options(header='false', delimiter='\t')\
    .schema(schema_lemm)\
    .load(path_lemm)

path_lexi = 'lexicon-it.csv'

schema_lexi = StructType([
    StructField("Type", StringType(), True),\
    StructField("Sentiment", StringType(), True),\
    StructField("Score", FloatType(), True),\
    StructField("Word", StringType(), True)])

lexi = spark.read.format('csv')\
    .options(header='false', delimiter=';')\
    .schema(schema_lexi)\
    .load(path_lexi)

lexi = lexi.drop('Type')

if TEST_MODE == 'true':
    path_path_valutation = PATH_TWEET_LABEL

    schema_valutation = StructType([
        StructField("Tweet_", StringType(), True), \
        StructField("Sentiment_", StringType(), True)])

    valutation = spark.read.format('csv') \
        .options(header='false', delimiter='\t') \
        .schema(schema_valutation) \
        .load(path_path_valutation)

path_tweets = PATH_TWEET

# MAIN #

time_ = time.time()

tweets = spark.sparkContext.textFile(path_tweets, minPartitions=NUMBER_PARTITIONS).zipWithIndex()
tweets = tweets.map(lambda line: (word_tokenize(re.sub(r'[\d-]', '', re.sub(r'[^\w\s]', ' ',\
            re.sub(r"(?:\@|http?\://|https?\://|www)\S+", "", line[0]))).lower()), line[1]))

stop_words = set(stopwords.words('italian'))

tweets = tweets.flatMap(lambda line: [(w, line[1]) for w in line[0] if not w in stop_words])
tweets = tweets.map(lambda line: (line[0], line[1]))

if not tweets.isEmpty():
    TableA = spark.createDataFrame(tweets, ['Word_', 'ID_Tweet'])
    TableB = lemm

    ta = TableA.alias('ta')
    tb = TableB.alias('tb')

    join_with_word = ta.join(tb, ta.Word_ == tb.Word)
    join_with_lemma = ta.join(tb, ta.Word_ == tb.Lemma)

    TableA = join_with_word.union(join_with_lemma)
    TableB = lexi

    ta = TableA.alias('ta')
    tb = TableB.alias('tb')

    join_with_lemma = ta.join(tb, ta.Lemma == tb.Word).drop_duplicates(["Word_", "ID_Tweet"])

    join_with_lemma = join_with_lemma.drop("Word", "Lemma", "Word_")

    word_score = join_with_lemma.rdd

    word_score = word_score.map(lambda line: (line[0], compute_score(line[1], line[2])))
    tweet_score = word_score.reduceByKey(lambda a, b: a + b, numPartitions=NUMBER_PARTITIONS)

    if not tweet_score.isEmpty():
        TableA = spark.createDataFrame(tweet_score, ['ID_Tweet', 'Score'])
        TableB = spark.createDataFrame(spark.sparkContext.textFile(path_tweets,\
                    minPartitions=NUMBER_PARTITIONS).zipWithIndex(), ['Tweet', 'ID_Tweet'])

        ta = TableA.alias('ta')
        tb = TableB.alias('tb')

        tweet_sentiment = tb.join(ta, ta.ID_Tweet == tb.ID_Tweet).drop("ID_Tweet")

        tweet = tweet_sentiment.rdd.map(lambda x: (x[0], x[1], compute_sentiment(x[1])))

        match = spark.createDataFrame(tweet, ['Tweet', 'Score', 'Sentiment']).dropDuplicates(["Tweet"])

        if TEST_MODE == 'true':
            TableA = match
            TableB = valutation

            ta = TableA.alias('ta')
            tb = TableB.alias('tb')

            match = ta.join(tb, ta.Tweet == tb.Tweet_, how='left').dropDuplicates(["Tweet"]).drop("Tweet_")

time_ = time.time() - time_

match = match.toPandas()
pandas.set_option('display.max_rows', match.shape[0]+1)

if TEST_MODE == 'true':
    path_output = "Comparison_"+ datetime.datetime.now().strftime("%d%b%Y.csv")
    match.to_csv(path_output, sep='\t', na_rep='None', index=False)

else:
    path_output = "Valutation_"+ datetime.datetime.now().strftime("%d%b%Y.csv")
    match.to_csv(path_output, sep='\t', na_rep='None', index=False)

print("\nTime analysis: " + str(time_))
print("Path file generated: " + path_output + "\n")
