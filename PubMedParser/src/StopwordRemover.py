from nltk import *
from nltk.corpus import stopwords

def removeStopwords(string, stopWordList=stopwords.words()):

    """
    Removes stopwords in accordance to the nltk stopwords corpus, we
    might consider the user to supply a stopword list to allow it to
    be customized.

    By sending a stop word list to the function it allows a user
    defined stop word list to be used instead of the standard nltk
    stop word corpus.
    """

    return ' '.join([word.strip() for word in string.split(' ') if word not in stopWordList]).strip()
