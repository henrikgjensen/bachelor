import urllib2
from BeautifulSoup import *
from urlparse import urljoin
import TextCleaner
import writeOut

# Get compiled regexps
removeTags=TextCleaner.removeHTMLTags()
removeNBSPs=TextCleaner.removeNPSBs()
removeRefs=TextCleaner.removeReferences()
removeSlashes=TextCleaner.removeSlashes()
removeCommas=TextCleaner.removeCommas()

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
        if 'uid' in key:
            key='from_uid'
        value=token[i+1:]
        dict[key]=value

    return dict

def fetchPubmedDiseaseTerms(pages):

    """
    Takes a URL-list of pages to crawl for pubmed terms, uids and optional
    describtions.

    Returns a dictionary on the form {DiseaseName:{uid:'',term:[],desc:''}}
    """

    pubmedURLs={}

    printvar=0
    pagenumber=0
    desccounter=0
    for page in pages:
        pagenumber+=1
        
        # Open the page
        try:
            c=urllib2.urlopen(page)
        except:
            print "Could not open %s" % page
            continue
        soup=BeautifulSoup(c.read())

        # Get disease name
        title=soup.html.head.title.string

        # Allocate dictionary
        pubmedURLs[title]={}
        pubmedURLs[title]['db']=''      # ..database to search in
        pubmedURLs[title]['terms']=''   # ..handcrafted search term
        pubmedURLs[title]['syn']=[]     # ..disease synonyms
        pubmedURLs[title]['uid']=''     # ..search id
        pubmedURLs[title]['desc']=''    # ..optional disease description

        # Check for Pubmed direct links
        links=soup('a')
        for link in links:
            if ('href' in dict(link.attrs)):
                urlString=link['href'].lower()
                # If there is a PubMed direct link and it's an id:
                if ((('pubmed') in urlString) & (('uid=') in urlString)):
                    tokens=_parseURL(urlString)
                    uid=tokens['from_uid']
                    pubmedURLs[title]['uid']=uid
                    pubmedURLs[title]['db']=tokens['db']
                    printvar+=1
                    print 'Found',str(printvar),'PubMed terms/uids.',title
                # If there is a PubMed direct link and it's a handcrafted term:
                if ((('pubmed') in urlString) & (('term=') in urlString)):
                    tokens=_parseURL(urlString)
                    terms=tokens['term']
                    pubmedURLs[title]['terms']=terms
                    pubmedURLs[title]['db']=tokens['db']
                    printvar+=1
                    print 'Found',str(printvar),'PubMed terms/uids.',title

        if ((pubmedURLs[title]['db']!='')&(pubmedURLs[title]['db']!='omim')&(pubmedURLs[title]['db']!='pubmed')):
            print "*****Found different db:",pubmedURLs[title]['db']

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
            print 'Total pages looked in:',str(pagenumber),'\nPages found:',str(printvar),'\nMissing for current letter:',(len(pages)-printvar),'\nDescriptions found:',str(desccounter)
            print '*****************************************************'
            print 'Writing to files...'
            # Write out and flush dictionary
            for disease in pubmedURLs:
                # Remove some problematic tokens from the file name
                disease=removeSlashes.sub(' ',disease)
                disease=removeCommas.sub(' ',disease)
                # Write out
                writeOut.writeOut("BA_DiseaseCrawler",disease,pubmedURLs[disease])
            pubmedURLs={}
            print 'Wrote successfully. Dictionary flushed.'