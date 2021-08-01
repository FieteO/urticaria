from wordcloud import WordCloud
from sklearn.feature_extraction import text
import matplotlib.pyplot as plt
import pandas as pd

# context specific keywords not to include in topic modelling
fsi_stop_words = [
  'sref', 'sbref', 'patient',
  'study', 'treatment', 'use',
]
df = pd.read_csv('./retrieval/Data/ImportFileList.csv')
urticaria = pd.read_csv('./retrieval/Data/ProcessedData.csv')

urticaria_urls_rows = df.loc[:, ['Name', 'path']].values.tolist()

# add Author names as stop words
for fsi in [row[0] for row in urticaria_urls_rows]:
    for t in fsi.split(' '):
        fsi_stop_words.append(t)

# our list contains all english stop words + article + specific keywords
stop_words = text.ENGLISH_STOP_WORDS.union(fsi_stop_words)

# aggregate all 7200 records into one large string to run wordcloud on term frequency
# we could leverage spark framework for TF analysis and call wordcloud.generate_from_frequencies instead
large_string = ' '.join(urticaria['lemma'])

# use 3rd party lib to compute term freq., apply stop words
word_cloud = WordCloud(
    background_color="white",
    max_words=5000,
    width=900,
    height=700,
    stopwords=stop_words,
    contour_width=3,
    contour_color='steelblue'
)

# display our wordcloud across all records
plt.figure(figsize=(10,10))
word_cloud.generate(large_string)
plt.imshow(word_cloud, interpolation='bilinear')
plt.axis("off")
plt.show()