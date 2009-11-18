from nltk import *


def wc(pmid, string):
    
    ll=[pmid,[]]

    fdist = FreqDist(word.lower() for word in string.split(' '))

    ll[1].extend(fdist.items())

    return ll
