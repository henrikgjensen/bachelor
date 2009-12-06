
import TFIDFMatrix
import Stemmer

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

    string=Stemmer.stem(string)

    return string
