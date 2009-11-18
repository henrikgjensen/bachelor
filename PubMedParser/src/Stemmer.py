from nltk import *
import re
from nltk.corpus import stopwords



def stem(string,cleanString=_cleanString,removeStopwords=_removeStopwords, stem=PorterStemmer().stem):

    forStemming = Text(removeStopwords(cleanString(string.lower())).split(' '))

    return ' '.join([stem(w) for w in forStemming if w != ''])
#    return [PorterStemmer().stem(w) for w in forStemming if w != '']


# Default string cleaner, it simply removes everything that is not
# alphabetic or or digit.
def _cleanString(string):

    return re.sub('[^\w]', ' ', string)

# Default stopword remover. Uses nltk default stopword list for
# identifying stopwords
def _removeStopwords(string):

    return ' '.join([word for word in string.split(' ') if word not in stopwords.words()])
