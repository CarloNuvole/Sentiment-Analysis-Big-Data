# ------------------------------------------------------------------------------
# Project: Sentiment Analysis for italian tweets using lexicon with Spark
#
# This .py is used to compute the overall accuracy and occurrencies for each
# label for the output file of sentiment.py.
#
# Input File Schema: Tweet Score Sentiment Label
# Input Parameters: <numbers_slave> <path>
#  - numbers_slave: number of AWS datanodes
#  - path: must be a 'tsv'
#
# Language used: Python
#
# Academic project (course: BIG DATA)
#
# (C) 2021 Carlo Nuvole & Luca Sedda, Università degli Studi di Cagliari, Italy
# Released under GNU Public License (GPL)
# ------------------------------------------------------------------------------

# LIBRARIES

import re
import sys
import time
import pandas

from pyspark.sql.functions import *
from pyspark.sql.types import *
from pyspark.sql import *

# FUNCTIONS

def compute_couple(x, y):
    if x == y:
        return ("Equal", 1)

    return ("Not_Equal", 1)

def compute_sentiment(x):
    if x == "POSITIVE":
        return ("Positive", 1)

    elif x == "NEGATIVE":
        return ("Negative", 1)

    return ("Neutral", 1)

# MAIN

NUMBER_PARTITIONS = int(sys.argv[1])

PATH = sys.argv[2]

spark = SparkSession.builder.appName('PySpark - Test Results').getOrCreate()
spark.sparkContext.setLogLevel('WARN')

schema = StructType([
    StructField("Tweet", StringType(), True), \
    StructField("Score", FloatType(), True), \
    StructField("Sentiment", StringType(), True), \
    StructField("Sentiment_", StringType(), True)])

val = spark.read.format('csv') \
    .options(header='true', delimiter='\t', index='true') \
    .schema(schema) \
    .load(PATH)

# Compute Accuracy

step_1 = val.rdd.map(lambda x: compute_couple(x[2], x[3]))
step_2 = step_1.reduceByKey(lambda a, b: a + b, numPartitions=NUMBER_PARTITIONS).collect()

if step_2[1][0] == 'Equal':
    a = step_2[1][1]
    b = step_2[0][1]
else:
    b = step_2[1][1]
    a = step_2[0][1]

acc = (a / (b + a)) * 100

# Compute Occurrency

step_1 = val.rdd.map(lambda x: compute_sentiment(x[2]))
step_2 = step_1.reduceByKey(lambda a, b: a + b, numPartitions=NUMBER_PARTITIONS)

table_1 = spark.createDataFrame(step_2, ['Sentiment', 'Occurrency'])

step_1 = val.rdd.map(lambda x: compute_sentiment(x[3]))
step_2 = step_1.reduceByKey(lambda a, b: a + b, numPartitions=NUMBER_PARTITIONS)

table_2 = spark.createDataFrame(step_2, ['Sentiment_', 'Occurrency_'])

ta = table_1.alias('ta')
tb = table_2.alias('tb')

table = ta.join(tb, ta.Sentiment == tb.Sentiment_).drop('Sentiment_')

print("\n")
print ("| Accuracy: " + "{:.2f}".format(acc) + " % ")
table.show()
print("\n")
