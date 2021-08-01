
import string
import re
import pandas as pd


from pyspark import SparkConf, SparkContext
from pyspark.sql import SparkSession
import pyspark.sql.functions as F
from pyspark.sql.types import *
from pyspark.sql.functions import col, pandas_udf, PandasUDFType, udf
import findspark

import spacy
import gensim
from tika import parser




def remove_non_ascii(text):
    printable = set(string.printable)
    return ''.join(filter(lambda x: x in printable, text))

def not_header(line):
    # as we're consolidating broken lines into paragraphs, 
    # we want to make sure not to include headers
    return not line.isupper()

def extract_statements(nlp, text):
  
    """
  Extracting desease statements from raw text by removing junk, URLs, etc.
  We group consecutive lines into paragraphs and use spacy to parse sentences.
    """
  
  # remove non ASCII characters
  
    text = remove_non_ascii(text)
  
    lines = []
    prev = ""
    for line in text.split('\n'):
    # aggregate consecutive lines where text may be broken down
    # only if next line starts with a space or previous does not end with dot.
        if(line.startswith(' ') or not prev.endswith('.')):
            prev = prev + ' ' + line
        else:
            # new paragraph
            lines.append(prev)
            prev = line
        
  # don't forget left-over paragraph
    lines.append(prev)

    # clean paragraphs from extra space, unwanted characters, urls, etc.
    # best effort clean up, consider a more versatile cleaner
    sentences = []
    for line in lines:

      # removing header number
      line = re.sub(r'^\s?\d+(.*)$', r'\1', line)
      # removing trailing spaces
      line = line.strip()
      # words may be split between lines, ensure we link them back together
      line = re.sub('\s?-\s?', '-', line)
      # remove space prior to punctuation
      line = re.sub(r'\s?([,:;\.])', r'\1', line)
      # remove figures that are not relevant to grammatical structure
      line = re.sub(r'\d{5,}', r' ', line)
      # remove mentions of URLs
      line = re.sub(r'((http|https)\:\/\/)?[a-zA-Z0-9\.\/\?\:@\-_=#]+\.([a-zA-Z]){2,6}([a-zA-Z0-9\.\&\/\?\:@\-_=#])*', r' ', line)
      # remove URLs part II
      line = re.sub(
          '(https?:\/\/(?:www\.|(?!www))[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\.[^\s]{2,}'
          '|www\.[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\.[^\s]{2,}|https?:\/\/(?:www\.|(?!www))[a-zA-Z0-9]+\.[^\s]{2,}'
          '|www\.[a-zA-Z0-9]+\.[^\s]{2,})',
          'link', line)
      # remove Refs
      line = re.sub('\[\d+(,\s{0,}\d+){0,}\]', '', line)
      # remove GhostChars
      line = re.sub(r'[^\x00-\x7F]+', ' ', line)
      # remove multiple spaces
      line = re.sub('\s+', ' ', line)
      # remove extra spaces
      line = re.sub(r'( +)', ' ', line)
      # remove brackets
      line = re.sub('(\(.*?\))|(\[.*?\])', '', line)

      # split paragraphs into well defined sentences using spacy
      for part in list(nlp(line).sents):
        sentences.append(str(part).strip())

    return sentences




def tokenize(sentence):
    gen = gensim.utils.simple_preprocess(sentence, deacc=True)
    return ' '.join(gen)

def lemmatize(nlp, text):
  
    # parse sentence using spacy
    doc = nlp(text) 

    # convert words into their simplest form (singular, present form, etc.)
    lemma = []
    for token in doc:
        if (token.lemma_ not in ['-PRON-']):
            lemma.append(token.lemma_)

    return tokenize(' '.join(lemma))




if __name__ == '__main__':

    df = pd.read_csv('./retrieval/Data/ImportFileList.csv')

    findspark.init()

    # Create SparkSession
    spark = SparkSession.builder\
        .master("local")\
        .appName("Uticaria_Spark")\
        .getOrCreate()

    urticaria_urls_rows = df.loc[:, ['Name', 'path']].values.tolist()

    # create a Pandas dataframe of Urticaria articles incl. path
    urticaria_path_pd = pd.DataFrame(urticaria_urls_rows, columns=['article', 'path'])

    # distribute the collection across the cluster to...
    # ...exploit parallelism when downloading / curating information

    @udf('string')
    def extract_content(path: str) -> str:
        try:

            raw = parser.from_file(path)
            return raw['content']
        except:
            return ""


    @udf('string')
    def extract_meta(path: str) -> str:

        try:
            raw = parser.from_file(path)
            return raw['metadata']
        except:
            return ""

    urticaria_urls = spark.createDataFrame(urticaria_path_pd).repartition(8)

    # cache PDFs
    urticaria_articles = urticaria_urls.withColumn('content', extract_content(F.col('path'))) \
        .withColumn('meta', extract_meta(F.col('path'))) \
        .filter(F.length(F.col('content')) > 0) \
        .cache()


    @pandas_udf('array<string>', PandasUDFType.SCALAR_ITER)
    def extract_statements_udf(content_series_iter):
        """
        as loading a spacy model takes time, we certainly do not want to load model for each record to process
        we load model only once and apply it to each batch of content this executor is responsible for
        """

        # load spacy model
        #spacy.cli.download("en_core_web_sm")
        nlp = spacy.load("en_core_web_sm", disable=['ner'])

        # cleanse and tokenize a batch of PDF content
        for content_series in content_series_iter:
            yield content_series.map(lambda x: extract_statements(nlp, x))


    """
                                # ******************************#
                                # apply transformation at scale #
                                # ******************************#
    """
    urticaria_statements = urticaria_articles.withColumn('statements', extract_statements_udf(F.col('content'))) \
        .withColumn('statement', F.explode(F.col('statements'))) \
        .filter(F.length(F.col('statement')) > 100) \
        .select('article', 'statement') \
        .cache()




    @pandas_udf('string', PandasUDFType.SCALAR_ITER)
    def lemma(content_series_iter):
        """
        as loading a spacy model takes time, we certainly do not want to load model for each record to process
        we load model only once and apply it to each batch of content this executor is responsible for
        """

        # load spacy model
        #spacy.cli.download("en_core_web_sm")
        nlp = spacy.load("en_core_web_sm", disable=['ner'])

        # lemmatize a batch of text content into sentences
        for content_series in content_series_iter:
            yield content_series.map(lambda x: lemmatize(nlp, x))


    """    
                                # ******************************#
                                # apply transformation at scale #
                                # ******************************#
    """

    urticaria_lemma = urticaria_statements.withColumn('lemma', lemma(F.col('statement'))) \
        .select('article', 'statement', 'lemma')

    urticaria = urticaria_lemma.select("article", "statement", "lemma").toPandas()

    urticaria.to_csv('./retrieval/Data/ProcessedData.csv')