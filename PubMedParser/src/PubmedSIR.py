from Bio import Entrez
from Bio import Medline
import urllib
import SearchTermCombiner as STC
import TextCleaner as TC

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

def work(diseaseDictionary):

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
    diseaseArticleIDlist={}

    for disease in diseaseDictionary:
        articleCount=250
        diseaseArticleIDlist[disease]=[]
        if (diseaseDictionary[disease]['terms'] != ''):
            diseaseArticleIDlist[disease].extend(getArticleIDlist(TC.unquoteString(diseaseDictionary[disease]['terms']),articleCount))
            print 'TEST TEST TEST TEST TEST TEST TEST TEST '
        elif (diseaseDictionary[disease]['uid'] != ''):
            diseaseArticleIDlist[disease].extend(getArticleIDsFromLink(diseaseDictionary[disease]['uid'],articleCount))

        articleCount-=len(diseaseArticleIDlist[disease])

        # If we still have qouta left
        if (articleCount > 0):
            # Search for the disease name on pubmed/medline
            diseaseArticleIDlist[disease].extend(getArticleIDlist(disease,articleCount))

        # Remove duplicates
        diseaseArticleIDlist[disease] = removeDuplicates(diseaseArticleIDlist[disease])

        # diseaseArticleIDlist, should contain about 250 PMIDs by now
        articleCount = 500 - len(diseaseArticleIDlist[disease])

        # Call SearchTermCombiner to combine search terms and adds hasabstract[text] behind it.
        diseaseDictionary[disease]['syn'] = STC.searchTermCombiner(diseaseDictionary[disease]['syn'])

        print 'Downloading into synonym list:'
        synonymArticleIDlist={}
        for synonym in diseaseDictionary[disease]['syn']:
            synonymArticleIDlist[synonym]=[]

            synonymArticleIDlist[synonym].extend(getArticleIDlist(TC.unquote(synonym),0))

#        if debug == True : print 'Completed download from synonym list'

        print synonymArticleIDlist

        print 'Sorting items accoring to their count by values()'
        # Needs to get the list sorted on the amount of return IDs.
        items = [(len(v),v,k) for k,v in synonymArticleIDlist.items()]

        items.sort()
        items.reverse()
        listIsEmpty = False

        print 'AC: ', articleCount
        print 'Adding additional PMIDs to list'
        while ((articleCount > 0) or (not listIsEmpty)):
            # Is the list empty, then break.

            print items
            if( items == [] ):
                print 'list is empty test???'
                listIsEmpty = True
                break
            # Test whether the next items makes articleCount
            # underflow, then we need to break
            elif ((articleCount - items[len(items)-1][0]) < 0):
                print 'underflow test???'
                break

            # items is sort largest to smallest, so pop the last one.
            resultTuple=items.pop()
            if(resultTuple[0] == 0):
                print 'Choose to contiue, because resulting tuple did not contain any results'
                continue

            print 'resultTuple', resultTuple
            # decrement articleCount with the number of PMIDs in the resulting tuple
            articleCount-=resultTuple[0]
            print 'Article count from while loop: ', articleCount
            # add the articleID to the total list.
            print 'Numbers added', resultTuple[0]
            print 'Added', resultTuple[1]
            print 'From syn', resultTuple[2]
            diseaseArticleIDlist[disease].extend(synonymArticleIDlist[resultTuple[2]])
            
            print 'THE WHILE LOOP THE WHILE LOOP THE WHILE LOOP '
            print disease + ': ', diseaseArticleIDlist[disease]
            print 'Length: ', len(diseaseArticleIDlist[disease])

#            print diseaseArticleIDlist[disease]

        # Special treatment for the last entry in synonymArticleIDlist
        # that made articleCount underflow and making sure the list is
        # not empty
        if (articleCount > 0) and not listIsEmpty:
            # From synonymArticleIDlist select the last element of
            # items (the one that made it underflow), look up the
            # term, and select the PMIDs from 0 to articleCount to
            # fill up the rest of the qouta
            diseaseArticleIDlist[disease].extend(synonymArticleIDlist[items[len(items)-1][2]][0:articleCount])
            print '========================================'
            print 'ArticleCount: ', articleCount
            print disease + ': ', diseaseArticleIDlist[disease]
            print 'Length: ', len(diseaseArticleIDlist[disease])

#        diseaseArticleIDlist[disease]['description'] = diseaseDictionary[disease]['desc']
        # Removing the duplicate PMIDs from the return list.
#        diseaseDictionary[disease]=removeDuplicates(diseaseDictionary[disease])

        return diseaseArticleIDlist

# From getArticlesFromSearchTerms(list of search terms)


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
