import TFIDFMatrix
import Stemmer
import StopwordRemover

def generateLogTFIDF(M_coo):

    """
    Creates a log TF-IDF term-doc matrix.
    """
    
    TFIDFMatrix.generateLogTFIDF(M_coo)


def porterStemmer(string):

    """
    Accepts a string and optionally a stemmer function working on
    single words, it defaults to the nltk PorterStemmer algorithm.

    Returns a stemmed string.
    """

    return Stemmer.stem(string)


def stopwordRemover(string):

    """
    Removes stopwords in accordance to the nltk stopwords corpus using
    english words, we might consider the user to supply a stopword
    list to allow it to be customized.

    By sending a stop word list to the function it allows a user
    defined stop word list to be used instead of the standard nltk
    stop word corpus.
    """

    return StopwordRemover.removeStopwords(string)

