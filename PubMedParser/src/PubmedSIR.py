from Bio import Entrez
from Bio import Medline
import urllib
import SearchTermCombiner as STC


def getArticleIDs(diseaseDictionary):

    """
    Takes a dictionary of the form:
    {'disease xx': {'terms' : [xx, yy], 'uid' : string, 'description' : string }, etc}}
    And returns a dictionary containing:
    {'disease a': [pmid1, pmid2, pmid3...], 'disease b' : [pmidx, pmidy,...], ...}

    Duplicate PMIDs are removed.
    """

    diseaseArticleIDlist = {}

    for disease in diseaseDictionary:
        diseaseArticleIDlist[disease]=[]

        if (diseaseDictionary[disease]['terms'] != []):
            for searchterm in diseaseDictionary[disease]['terms']:
                diseaseArticleIDlist[disease].extend(getArticleIDlist(searchterm,0))

        if (diseaseDictionary[disease]['uid'] != ''):
            print 'Downloading from %s uid' % disease, diseaseDictionary[disease]['uid']
            diseaseArticleIDlist[disease].extend(getArticleIDsFromLink(diseaseDictionary[disease]['uid']))

        diseaseArticleIDlist[disease]['description'] = diseaseDictionary[disease]['desc']
        # Removing the duplicate PMIDs from the return list.
        diseaseDictionary[disease]=removeDuplicates(diseaseDictionary[disease])

    return diseaseArticleIDlist

def getTheCorrectNumberOfArticles(diseaseDictionary):

    """
    Takes a dictionary of the form:
    {'disease xx': {'syn' : [xx, yy], 'term' : string, 'uid' : string, 'description' : string }, etc}}
    And returns a dictionary containing:
    {'disease a': [pmid1, pmid2, pmid3...], 'disease b' : [pmidx, pmidy,...], ...}

    Where disease xx is the name of the disease, syn is a list of
    synonyms, term is a hand crafted search term (if it exists),
    description is the description from the rarediseases.info (if it
    exists).

    Duplicate PMIDs are removed.
    """

    # Iterates through the diseaseDictionary and searches for uid,
    # term, diseasename, and combinations of synonyms
    for disease in diseaseDictionary:
        articleCount=250
        diseaseArticleIDlist[disease]=[]

        if (diseaseDictionary[disease]['terms'] != ''):
            diseaseArticleIDlist[disease].extend(getArticleIDlist(diseaseDictionary[disease]['term'],articleCount))
        elif (diseaseDictionary[disease]['uid'] != ''):
            diseaseArticleIDlist[disease].extend(getArticleIDsFromLink(diseaseDictionary[disease]['uid'],articleCount))

        articleCount-=len(diseaseArticleIDlist[disease])

        if (articleCount > 0):
            diseaseArticleIDlist[disease].extend(getArticleIDlist(disease),articleCount)

        # Remove duplicates

        # diseaseArticleIDlist, should contain about 250 PMIDs by now
        articleCount = 500 - len(diseaseArticleIDlist[disease])

        # Call SearchTermCombiner to combine search terms and adds hasabstract[text] behind it.
        diseaseDictionary['syn'] = STC.searchTermCombiner(diseaseDictionary['syn'])

        synonymArticleIDlist={}
        for synonym in diseaseDictionary[disease]['syn']:
            synonymArticleIDlist[synonym]=[]

            synonymArticleIDlist[synonym] = getArticleIDlist(diseaseDictionary[disease][synonym])

        for synonym in sorted(synonymArticleIDlist.values())

        if (diseaseDictionary[disease]['uid'] != ''):
            print 'Downloading from %s uid' % disease, diseaseDictionary[disease]['uid']
            diseaseArticleIDlist[disease].extend(getArticleIDsFromLink(diseaseDictionary[disease]['uid']))

        diseaseArticleIDlist[disease]['description'] = diseaseDictionary[disease]['desc']
        # Removing the duplicate PMIDs from the return list.
        diseaseDictionary[disease]=removeDuplicates(diseaseDictionary[disease])




def getLeastSearchResults(listOfSearchTerms):

    """
    We want to minimize the number of articles return, so we try alot
    of different search terms, from the synonym list. Do not want to
    get 0 articles back either, we want to find the golden middle way.
    """

    listOfresults = []

    for term in listOfSearchTerms:
        count = getArticleCount(term)
        print 'Search term: ' + term + ' resulted in ' + count + ' number of articles'
        listOfresults.append(int(getArticleCount(term)))

    return listOfSearchTerms[min(map(_addabunch, listOfresults))]

# Helper function that returns 35000000 to x if x equals 0. Used to weed
# out search terms resulting in zero articles.
def _addabunch(x):
    if x == 0:
        return 35000000
    else:
        return x

def removeDuplicates(listOfIDs):
    """
    Quick and dirty hack to remove duplicates from list using
    dictionary, this should be pretty fast. But it does not preserve
    the ordering. Which is of no use anyways.
    """

    d = {}

    for x in listOfIDs: d[x] = x

    listOfIDs = d.values()

    return listOfIDs

def getArticleIDsFromLink(uid, number_of_articles=20):

    """
    Helper function that is able to handle the special type of links
    that are sometimes returned by rarediseasesdatabase.com, it
    recieves a "uid" and returns all the pubmed IDs containing
    an abtract.
    """

    Entrez.email = 'michael@diku.dk'

    if number_of_articles==0 : number_of_articles=int(getArticleCount(search_term))

    handle=Entrez.elink(db='omim', LinkName='omim_pubmed_calculated', from_uid=uid, retmax=number_of_articles)
    results = Entrez.read(handle)

    ids = [link['Id'] for link in results[0]['LinkSetDb'][0]['Link']]

    return ids


def getArticleCount(search_term):

    """
    This function takes search terms and returns the total number of
    found articles in the PubMed database.
    """

    Entrez.email = 'henrikgjensen@gmail.com'

    handle=Entrez.esearch(db='pubmed',term=search_term,retmax='0')
    record=Entrez.read(handle)
    retmax_length=record['Count']
    print 'Counted a total of',retmax_length,'articles'
    return retmax_length

def getArticleIDlist(search_term,number_of_articles=20):

    """
    This function takes search terms and an integer representing how
    many articles that should be searched for. A list of article-ids
    is returned.  If no number is given, 20 articles will be
    returned. If 0 is given, all articles found will be returned.
    """

    Entrez.email = 'henrikgjensen@gmail.com'

    if number_of_articles==0 : number_of_articles=int(getArticleCount(search_term))

    pmids=[]
    for i in range(0,int(number_of_articles),100000):
        handle=Entrez.esearch(db='pubmed',term=search_term,
            retmax=number_of_articles,retstart=i)
        record=Entrez.read(handle)
        pmids.extend(record['IdList'])
        print 'Downloaded',len(pmids),'PMIDs.',str(number_of_articles-len(pmids)),'remaining...'
    return pmids


def getMedlineList(pmids):

    """
    This function takes a list of article-ids and returns a list of MedLine
    articles that contains an abstract.
    """

    records = []
    cleaned_records = []
    listLength = len(pmids)

    Entrez.email = 'henrikgjensen@gmail.com'

    for i in range(0, listLength, 650):
        tempList = pmids[i:i + 650]
        handle = Entrez.efetch(db='pubmed', id=tempList,rettype='medline', retmode='text')
        records.extend(list(Medline.parse(handle)))
        print 'Downloaded',len(records),'MedLine articles.',str(listLength-len(records)),'remaining...'

    for article in records:
        if 'AB' in article:
            cleaned_records.append(article)
    
    print 'Returned',len(cleaned_records),'MedLine articles containing an abstract.'
    return cleaned_records

def writeOut(list):
    count=0
    out=file('data.txt','w')
    for i in list:
        out.write(str(i)+'\n')
        count+=1
        print 'Wrote out liste element ',str(count)
        
"""
def printRecords(records):

    # Recieves a list of records and prints title, author (if it
    # exists) and source (if it exists)

    for record in records:
        print 'title:', record['TI'].lower()
        if 'AU' in record:
            print 'author:', record['AU']
        if 'SO' in record:
            print 'source:', record['SO']
        print

def print_abstracts(records):

    # Recives a list of records and prints title and abstract (if it
    # exists)

    for record in records:
        print 'title:', record['TI']
        if 'AB' in record:
            print 'abstract:', record['AB']
"""
