import re
import time
import urllib
import urllib2
from BeautifulSoup import *
from urlparse import urljoin


def fetchPubmedDiseaseURLs():

    diseaseURLs=[]
    pages=['A']#,'B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','Z','0-49']

    # Get a list of rare-disease URLs
    for index in pages:
        page='http://rarediseases.info.nih.gov/RareDiseaseList.aspx?StartsWith=%s' % index

        try:
            c=urllib2.urlopen(page)
        except:
            print "Could not open %s" % page
            continue

        soup=BeautifulSoup(c.read())
        links=soup('a')
        count=0
        for link in links:
            if ('id' in dict(link.attrs)):
                if ('ctrlRareDiseaseList' in link['id']) & ('Condition' in link['href']):
                    diseaseURLs.append(urljoin(page,link['href']))
                    count+=1

        print index,'completed.',count,'diseases added to list.'

    return diseaseURLs


def fetchPubmedFromNLM(href='http://gateway.nlm.nih.gov/gw/Cmd'):

    try:
        c=urllib2.urlopen(href)
        print 'Opened',href
    except:
        print "Could not open %s" % href


    #soup=BeautifulSoup(c.read())


    #links=soup('a')
    
    values={'UserSearchText':'Acrofacial dysostosis atypical postaxial'}

    data = urllib.urlencode(values)
    req = urllib2.Request(href, data)
    response = urllib2.urlopen(req)
    the_page = response.read()

    
    print the_page


def fetchPubmedDiseaseTerms(pages):
    # Go through the URL list and fetch PubMed related search terms

    pubmedURLs={}
    pubmedURLs['uid']=[]
    pubmedURLs['terms']=[]
    pubmedURLs['desc']=[]

    printvar=0
    for page in pages:
        try:
            c=urllib2.urlopen(page)
        except:
            print "Could not open %s" % page
            continue
        soup=BeautifulSoup(c.read())

        # Get disease name
        title=soup.html.head.title.string

        found=False
        links=soup('a')
        for link in links:
            if ('href' in dict(link.attrs)):
                urlString=link['href'].lower()
                # If there is a PubMed direct link and it's an id:
                if ((('pubmed') in urlString) & (('uid=') in urlString)):
                    strIndex=urlString.find('uid=')+4
                    urlString=urlString[strIndex:]
                    pubmedURLs['uid'].append(urlString)
                    printvar+=1
                    found=True
                    print 'Found',str(printvar),'PubMed terms/uids.',title
                # If there is a PubMed direct link and it's a term:
                if ((('pubmed') in urlString) & (('term=') in urlString)):
                    strIndex=urlString.find('term=')+5
                    urlString=urlString[strIndex:]
                    pubmedURLs['terms'].append(urlString)
                    printvar+=1
                    found=True
                    print 'Found',str(printvar),'PubMed terms/uids.',title

        # If no direct pubmed link was found, replace with title
        if (not found):
            title=title+' AND hasabstract[text]'
            pubmedURLs['terms'].append(title)

        # Disease synonyms are also added to the term list
        lis=soup('li')
        for li in lis:
            if ('synonym' in str(li.parent)):
                synonym=li.contents[0]+' AND hasabstract[text]'
                pubmedURLs['terms'].append(synonym)
                print '   ' + synonym

        # Look for a optional disease description
        descs=soup('span')
        for desc in descs:
            if ('id' in dict(desc.attrs)):
                idString=desc['id'].lower()
                if (('descriptionquestion' in idString) & ('#003366' not in str(desc))):
                    pubmedURLs['desc'].append(desc)
                    print '*Found optional disease description'

        print ''

    print 'Total pages looked in:',len(pages),'\nPages found:',str(printvar),'\nMissing:',(len(pages)-printvar),'\nDescriptions found:',len(pubmedURLs['desc'])

        
        


        #print soup.prettify()

    