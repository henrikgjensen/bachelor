from nltk import *

def stem(string,stem=PorterStemmer().stem):
    """
    Accept a string and optionally a stemmer function working on
    single words, it defaults to the nltk PorterStemmer algorithm.

    Return a combined string.
    """

    forStemming = Text(string.lower().split(' '))

    return ' '.join([stem(w.strip()) for w in forStemming if w != ''])


def stem(stringList,stem=PorterStemmer().stem):
    """
    Accept a list of strings and optionally a stemmer function working
    on single words, it defaults to the nltk PorterStemmer algorithm.

    Return a list of stemmed strings.
    """

    forStemming = Text([w.lower() for w in stringList])

    return [stem(w.strip()) for w in forStemming if w != '']
