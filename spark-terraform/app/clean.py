# ------------------------------------------------------------------------------
# Project: Sentiment Analysis for italian tweets using lexicon with Spark
#
# This .py is used to generate .csv
#
# Input Parameters: <path_input_file> <name_output_file>
#  - path_input_file
#  - <name_output_file> without '.csv'
#
# Language used: Python
#
# Academic project (course: BIG DATA)
#
# (C) 2021 Carlo Nuvole & Luca Sedda, Università degli Studi di Cagliari, Italy
# Released under GNU Public License (GPL)
# ------------------------------------------------------------------------------

import sys
import pandas as pd

if len(sys.argv) > 1:
    data = pd.read_csv(sys.argv[1], sep=',')

if len(sys.argv) > 2:
    file = open(sys.argv[2]+'_label.csv', 'w')
    file_2 = open(sys.argv[2]+'.csv', 'w')

    with pd.option_context('display.max_rows', None, 'display.max_columns', None, 'display.max_colwidth', None):
        for index, row in data.iterrows():
            file.write(row['tweet_text'].replace("\r", " ").replace("\n", " ").replace("\t", " ")\
                       .replace("\\", " ").replace("\"","") + "\t" + str(row['sentiment']) + "\n")
            file_2.write(row['tweet_text'].replace("\r", " ").replace("\n", " ").replace("\t", " ")\
                         .replace("\\", " ").replace("\"","") + "\n")

    file.close()
    file_2.close()