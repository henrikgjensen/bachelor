import urllib2
from BeautifulSoup import *
from urlparse import urljoin
from time import strftime, sleep
import TextCleaner
import IOmodule
import os

# Pages to be crawled (by default).
defaultPages=['0','A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','Z']

def fetchOprhanetDiseaseURLs(pages=defaultPages):

    """
    Takes a list of letters representing the pages to be crawled for rare
    diseases on http://www.orpha.net.

    Returns a list of URLs linking to describtive pages of the diseases found.

    The default list is:
    ['0','A','B','C','D','E','F','G','H','I','J','K','L','M',
    'N','O','P','Q','R','S','T','U','V','W','Z']
    """

    diseaseURLs=[]

    # Get a list of rare-disease URLs
    for index in pages:
        page='http://www.orpha.net/consor/cgi-bin/Disease_Search_List.php?lng=EN&TAG=%s' % index

        try:
            c=urllib2.urlopen(page)
        except:
            print "Could not open %s" % page
            continue

        soup=BeautifulSoup(c.read())
        links=soup('a')
        count=0
        for link in links:
            if 'href' in dict(link.attrs):
                if 'OC_Exp.php?lng=EN&Expert' in link['href']:
                    diseaseURLs.append(urljoin(page,link['href']))
                    count+=1

        print index,'completed.',count,'diseases added to list.'

    return diseaseURLs


def fetchOrphanetDiseaseTerms(pages):

    """
    Takes a URL-list of pages to crawl for ...

    Returns a dictionary on the form ...
    """

    diseaseURLs={}



    user_agent = 'Mozilla/5.0 (X11; U; Linux i686) Gecko/20071127 Firefox/2.0.0.11'
    user_agent = 'Mozilla/5.0 (X11; U; Linux x86_64; en-US; rv:1.9.0.15) Gecko/2009102815 Ubuntu/9.04 (jaunty) Firefox/3.0.15'
    headers = { 'User-Agent' : user_agent, 'Accept': 'text/xml,application/xml,application/xhtml+xml,text/html;q=0.9,text/plain;q=0.8,image/png,*/*;q=0.5','Accept-Language': 'en-gb,en;q=0.5','Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.7','Connection': 'keep-alive'}

    printvar=0
    pagenumber=0
    desccounter=0
    for page in pages:
        sleep(3)
        pagenumber+=1

        # Open the page.
        for i in range(3):
            try:
                req=urllib2.Request(page)
                data=''
                c=urllib2.urlopen(req,data,headers)
            except:
                print "Could not open %s" % page
                print "Attempt",str(i+1),"out of 3"
                #sleep(7)
                if i==2:
                    print "Could not open page. Terminating.."
                    raise StopIteration()

        try:
            soup=BeautifulSoup(c.read())
        except HTMLParseError:
            print 'Experienced difficulties opening %s' % page
            continue

        # Get disease name.
        title=soup.html.head.title.string[10:]

        print title

        # Allocate dictionary.
        diseaseURLs[title]={}
        diseaseURLs[title]['syn']=[]
        diseaseURLs[title]['desc']=''


        for header in soup('div'):
            if 'class' in dict(header.attrs):
                if header['class']=='article':
                    print header.contents[2]

    