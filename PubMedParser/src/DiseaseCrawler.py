import urllib2
from BeautifulSoup import *
from urlparse import urljoin
from time import strftime, sleep
import TextCleaner
import IOmodule
import os

# Get compiled regexps
removeTags=TextCleaner.removeHTMLTags()
removeNBSPs=TextCleaner.removeNPSBs()
removeRefs=TextCleaner.removeReferences()
removeSlashes=TextCleaner.removeSlashes()
removeCommas=TextCleaner.removeCommas()
removeWhitespaces=TextCleaner.removeWhitespaces()

# Folders to save downloaded diseases in
diseaseFolder="BA_DiseaseCrawler"
errorFolder="URL_error_log"

# Pages to be crawled (by default)
defaultPages=['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','Z','0-49']

def fetchPubmedDiseaseURLs(pages=defaultPages):

    """
    Takes a list of letters representing the pages to be crawled for rare
    diseases on http://rarediseases.info.nih.gov.
    
    Returns a list of URLs to be crawled for pubmed terms, uids and optional
    describtions.

    The default list is:
    ['A','B','C','D','E','F','G','H','I','J','K','L','M',
    'N','O','P','Q','R','S','T','U','V','W','Z','0-49']
    """

    diseaseURLs=[]
    
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

def _cleanString(desc):

    """
    Takes a string and removes html tags, selected expressions and references.

    Returns the 'cleaned' string.
    """

    desc=removeTags.sub('',desc)
    desc=removeNBSPs.sub(' ',desc)
    desc=removeRefs.sub('',desc)

    return desc

def _parseURL(url):

    """
    Takes a url and breakes it up into tokens.

    Returns dictionary on the form {'term'|'from_uid':term|uid}
    """
    dict={}

    shortenedURL=url[(url.find('?')+1):]
    tokenizedURL=shortenedURL.split('&')
    for token in tokenizedURL:
        i=token.find('=')
        key=token[:i]
        if 'term' in key:
            key='term'
        if ('uid' in key) | ('idsfromresult' in key) | ('list_uids' in key):
            key='from_uid'
        if 'dbfrom' in key:
            key='db'
        value=token[i+1:]
        # Whitespaces sometimes occur in the urls and to avoid later confusion
        # these are removed.
        if '%20' in value:
            value=removeWhitespaces.sub('',value)
        dict[key]=value

    return dict

def fetchPubmedDiseaseTerms(pages):

    """
    Takes a URL-list of pages to crawl for pubmed terms, uids and optional
    describtions.

    Returns a dictionary on the form:
    {DiseaseName:{db='',terms:'',syn=[],uid:'',desc:''}}
    """

    pubmedURLs={}
    problematicURLs=[]

    printvar=0
    pagenumber=0
    desccounter=0
    for page in pages:
        pagenumber+=1
        
        # Open the page
        for i in range(3):
            try:
                c=urllib2.urlopen(page)
            except:
                print "Could not open %s" % page
                print "Attempt",str(i+1),"out of 3"
                sleep(5)
                if i==2:
                    print "Could not open page. Terminating.."
                    raise StopIteration()

        try:
            soup=BeautifulSoup(c.read())
        except HTMLParseError:
            print 'Experienced difficulties opening %s' % page
            IOmodule.writeOut(diseaseFolder+'/'+errorFolder,strftime('%H%M%S'),page)
            continue

        # Get disease name
        title=soup.html.head.title.string

        # Some pages are 'officially' not working. Catch them here
        if title=='NIH Office of Rare Diseases Research (ORDR) - Error':
            IOmodule.writeOut(diseaseFolder+'/'+errorFolder,'Page error'+strftime('%H%M%S'),page)
            print 'Page Error on %s' % page
            continue

        # Allocate dictionary
        pubmedURLs[title]={}
        pubmedURLs[title]['db']='pubmed'    # ..database to search in (pubmed by default)
        pubmedURLs[title]['terms']=''       # ..handcrafted search term
        pubmedURLs[title]['syn']=[]         # ..disease synonyms
        pubmedURLs[title]['uid']=''         # ..search id
        pubmedURLs[title]['desc']=''        # ..optional disease description

        # Check for Pubmed direct links
        links=soup('a')
        found=False
        for link in links:
            if (link.contents):
                if ((link.contents[0] == 'PubMed')) & ('href' in dict(link.attrs)):
                    urlString = link['href'].lower()
                    # If there is a PubMed direct link and it's an id:
                    if ('uid=' in urlString) | ('uids=' in urlString) | ('idsfromresult=' in urlString):
                        tokens = _parseURL(urlString)
                        uid = tokens['from_uid']
                        pubmedURLs[title]['uid'] = uid
                        pubmedURLs[title]['db'] = tokens['db']
                        printvar += 1
                        found = True
                        print 'Found', str(printvar), 'PubMed terms/uids.', title
                        continue
                    # If there is a PubMed direct link and it's a handcrafted term:
                    elif ('term=' in urlString):
                        tokens = _parseURL(urlString)
                        terms = tokens['term']
                        pubmedURLs[title]['terms'] = terms
                        pubmedURLs[title]['db'] = tokens['db']
                        printvar += 1
                        found = True
                        print 'Found', str(printvar), 'PubMed terms/uids.', title
                        continue
                    # Special case 1: If there is a PubMed direct link but the uid is not part of the tokens
                    elif ('/entrez/' not in urlString):
                        start = urlString.find('/pubmed/') + 8
                        if '?' in urlString:
                            end = urlString.find('?')
                            uid = urlString[start:end]
                        else:
                            uid = urlString[start:]
                        print uid
                        pubmedURLs[title]['uid'] = uid
                        printvar += 1
                        found = True
                        print 'Found', str(printvar), 'PubMed terms/uids.', title, '. (Special case 1: No tokens)'
                    # Special case 2: If there is a webenv, the url is (by experience) not working but the disease name is still valuable for a pbumed search
                    elif '&webenv=' in urlString:
                        printvar += 1
                        found = True
                        print 'Found', str(printvar), 'PubMed terms/uids.', title, '. (Special case 2: WebEnv)'

                # Terminate if an unexpected url shows up
                if link.contents:
                    if (not found) & (link.contents[0]=='PubMed'):
                        print 'Could not fetch url'
                        raise StopIteration()

        # A simple addition to the printouts
        if not found:
            printvar+=1
            print 'Found',str(printvar),'Diseases.',title,'(no uid or term).'

        # Notify if an unexpected database shows up
        if ((pubmedURLs[title]['db']!='')&(pubmedURLs[title]['db']!='omim')&(pubmedURLs[title]['db']!='pubmed')):
            print "*****Found different db:",pubmedURLs[title]['db']
            print 'Could not fetch url'
            raise StopIteration()

        # Disease synonyms are also added to the term list
        lis=soup('li')
        for li in lis:
            if ('synonym' in str(li.parent)):
                synonym=li.contents[0]
                if (',') in str(synonym):
                    aditionalSynonyms=synonym.split(',')
                    for syn in aditionalSynonyms:
                        pubmedURLs[title]['syn'].append(syn)
                        print '  ' + syn
                else:
                    pubmedURLs[title]['syn'].append(synonym)
                    print '  ' + synonym

        # Look for a optional disease description on rarediseases.info.nih.gov
        descs=soup('span')
        for desc in descs:
            if ('id' in dict(desc.attrs)):
                idString=desc['id'].lower()
                if (('descriptionquestion' in idString) & ('#003366' not in str(desc))):
                    desc=_cleanString(str(desc))
                    pubmedURLs[title]['desc']=desc
                    desccounter+=1
                    print '    *Found optional disease description'
        print ''
        
        if ((pagenumber%20)==0):
            # Print status report
            print '*****************************************************'
            print 'Total pages looked in:',str(pagenumber),'\nPages found:',str(printvar),'\nRemaining in total:',(len(pages)-printvar),'out of',len(pages),'\nDescriptions found:',str(desccounter)
            print '*****************************************************'
            print 'Writing to files...'
            # Write out and flush dictionary
            for disease in pubmedURLs:
                # Remove some problematic tokens from the file name
                content=pubmedURLs[disease]
                disease=removeSlashes.sub(' ',disease)
                disease=removeCommas.sub(' ',disease)
                # Write out
                IOmodule.writeOut(diseaseFolder,disease,content)
            pubmedURLs={}
            print 'Wrote successfully. Dictionary flushed.'

def readDiseases(indexStart=0,indexStop=None):

    """
    Function for returning the content of all or some of the crawled diseases.

    By default all are returned in a dictionary of diseases on the form:
    {DiseaseName:{db='',terms:'',syn=[],uid:'',desc:''}}
    """

    path=os.getenv("HOME")+'/'+diseaseFolder+'/'

    files=sorted([f for f in os.listdir(path) if os.path.isfile(path+f)])

    contents={}
    for file in files[indexStart:indexStop]:
        diseaseName=file[0:file.find('.')]
        diseaseAttr=eval(open(path+file,'r').read())
        contents[diseaseName]=diseaseAttr
        
    return contents