from nltk import *

def stem(string,stem=PorterStemmer().stem):

    """
    Accepts a string and optionally a stemmer function working on
    single words, it defaults to the nltk PorterStemmer algorithm.

    Returns a combined string.
    """

    forStemming = Text(string.lower().split(' '))

    return ' '.join([stem(w.strip()) for w in forStemming if w != ''])
