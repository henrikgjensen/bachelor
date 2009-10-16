import re
import urllib

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

def unquoteString(string):
    # Replace '%xx' and '+' from search term, removes URL encoding of
    # string. E.g. %2F get replaced with '/' and '+' with ' '
    return urllib.unquote_plus(string)
