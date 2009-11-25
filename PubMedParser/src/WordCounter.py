from nltk import *
from TextCleaner import sanitizeString


def wc(pmid, string):
    
    ll=[pmid,[]]

    # Get the regex pattern that sanitizeses strings.
    p = sanitizeString()

    # Sanitize and remove empty strings ''
    fdist = FreqDist([word.lower() for word in p.sub(' ', string).split(' ') if word != ''])

    ll[1].extend(fdist.items())

    return ll
