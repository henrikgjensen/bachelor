import re
import urllib
from nltk.corpus import stopwords

def removeHTMLTags():
    """
    Returns a regular expression for removing HTML tags
    """
    return re.compile(r'<.*?>')

def removeNPSBs():
    """
    Returns a regular expression for removing &nbsp;
    """
    return re.compile(r'&nbsp;')

def removeReferences():
    """
    Returns a regular expression for removing references: [integer]
    """
    return re.compile(r'[\[0-9\]]')

def removeSlashes():
    """
    Returns a regular expression for removing /
    """
    return re.compile(r'/')

def removeCommas():
    """
    Returns a regular expression for removing ,
    """
    return re.compile(r',')

def removeWhitespaces():
    """
    Returns a regular expression for removing whitespaces
    """
    return re.compile(r'%20')

def unquoteString(string):
    """
    Used for replacing '%xx' and '+' from search terms, removes URL
    encoding of string. E.g. %2F is replaced with '/' and '+' with '
    '. For more information please read the urllib documentation.
    """

    return urllib.unquote_plus(string)

def decodeURLcharacters(string):
    """
    Used for decoding '&#xx;' from a string and return the decoded
    string. It uses an anonymous function for looking up the correct
    unicode character to replace '&#xx;' with.

    This might fail in some cases, where there are '&#xxxx;', and x is
    number. This requires an addition encoding with utf-8.
    """

    return re.sub(u'&#(\d+);', lambda x: unichr(int(x.group(1))),string)

def sanitizeString():
    """
    Returns a pattern that matches non-alphabetic and non-digit
    characters. Used for sanitizing string e.g. 'The dog is not red,
    but has a large tail' -> 'The dog is not red  but has a large tail'
    """

    return re.compile('[\W]')

def removeStopwords(string):
    """
    Removes stopwords in accordance to the nltk stopwords corpus, we
    might consider the user to supply a stopword list to allow it to
    be customized.

    Add that later.
    """

    return ' '.join([word.strip() for word in string.split(' ') if word not in stopwords.words()]).strip()
