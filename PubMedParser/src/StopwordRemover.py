from nltk import *
from nltk.corpus import stopwords

def removeStopwords(string):

    """
    Removes stopwords in accordance to the nltk stopwords corpus, we
    might consider the user to supply a stopword list to allow it to
    be customized.

    Add that later.
    """

    return ' '.join([word.strip() for word in string.split(' ') if word not in stopwords.words()]).strip()
