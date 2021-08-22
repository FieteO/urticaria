# https://stackoverflow.com/questions/39086/search-and-replace-a-line-in-a-file-in-python#315088
import re
import fileinput
import sys

"""
Spacy train prints out the training metrics to the command line.
This script formats the train.tsv file when copied from the command line.
"""
file = 'spacy_train_bc5.tsv'
for line in fileinput.input(file, inplace=1):
    line = re.sub('LOSS TOK2VEC', 'LOSS_TOK2VEC', line)
    line = re.sub('LOSS NER', 'LOSS_NER', line)
    line = re.sub('-+', '', line)
    line = re.sub('^ +', '', line)
    line = re.sub(' +', '\t', line)
    line = re.sub('^\n$','',line)
    line = re.sub('\t$','',line)
    sys.stdout.write(line)
