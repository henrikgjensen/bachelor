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
    #  ^ Need to update this one. ^

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

    # ^ Needs to be updated or removed ^

    # Iterates through the diseaseDictionary and searches for uid,
    # term, diseasename, and combinations of synonyms
    diseaseArticleIDlist={}

    for disease in diseaseDictionary:
        articleCount=250
        diseaseArticleIDlist[disease] = {}
        diseaseArticleIDlist[disease]['PMIDs']=[]
        diseaseArticleIDlist[disease]['description'] = ''
        if (diseaseDictionary[disease]['terms'] != ''):
            diseaseArticleIDlist[disease]['PMIDs'].extend(getArticleIDsFromMultiSource(diseaseDictionary[disease]['db'],'',TC.unquoteString(diseaseDictionary[disease]['terms']),articleCount))
        elif (diseaseDictionary[disease]['uid'] != ''):
            diseaseArticleIDlist[disease]['PMIDs'].extend(getArticleIDsFromMultiSource(diseaseDictionary[disease]['db'],diseaseDictionary[disease]['uid'],'',articleCount))

        articleCount = articleCount - len(diseaseArticleIDlist[disease]['PMIDs'])

        # If we still have qouta left
        if (articleCount > 0):
            # Search for the disease name on pubmed/medline
            diseaseArticleIDlist[disease]['PMIDs'].extend(getArticleIDsFromMultiSource('pubmed','',disease,articleCount))

        # Remove duplicates
        diseaseArticleIDlist[disease]['PMIDs'] = removeDuplicates(diseaseArticleIDlist[disease]['PMIDs'])

        # diseaseArticleIDlist, should contain about 250 PMIDs by now,
        # but we have a max limit on 500 articles, therefore we wish
        # to fill up with the other search form now. (By searching on
        # synonyms)
        articleCount = 500 - len(diseaseArticleIDlist[disease]['PMIDs'])

        # Call SearchTermCombiner to combine search terms and adds hasabstract[text] behind it.
        diseaseDictionary[disease]['syn'] = STC.searchTermCombiner(diseaseDictionary[disease]['syn'])

#        print 'Downloading into synonym list:'
        synonymArticleIDlist={}
        for synonym in diseaseDictionary[disease]['syn']:
            synonymArticleIDlist[synonym]=[]

#            synonymArticleIDlist[synonym].extend(getArticleIDlist(TC.unquoteString(synonym) ,0))
            synonymArticleIDlist[synonym].extend(getArticleIDsFromMultiSource('pubmed', '', TC.unquoteString(synonym) ,0))

#        if debug == True : print 'Completed download from synonym list'

        print 'Sorting items accoring to their count by values()'
        # Needs to get the list sorted on the amount of return IDs.
        items = [(len(v),v,k) for k,v in synonymArticleIDlist.items()]
        # Sort according to the length of the lists withing the tuples
        items.sort()
        # Reverse to get largest to smallest in list
        items.reverse()
#        print items

        listIsEmpty = False

        # Gonna make a list of maximum 250 PMIDs from the synonym list, without duplicates. As set contains unordered, unique elements, 
        collectionSet = set()

        # We might consider changing this, because right now, we check twice to see whester collectionSet exceeds articleCount
        while len(collectionSet) <= articleCount or not listIsEmpty:

            # Is the list of items empty, then we can't do anything.
            if items == []:
                listIfEmpty = True
                break
            # Does the next range of items exceed 250 PMIDs?
#            elif len(collectionSet) + items[len(items)-1][0] > 250:
#                break

            transferTuple = items.pop()

            # If 
            if transferTuple[0] == 0:
#                print 'Choose to contiue, because resulting tuple did not contain any results'
                continue

            for pmid in transferTuple[1]:
                # Test to see if len of the set is articleCount?
                if len(collectionSet) == articleCount:
                    break
                collectionSet.add(pmid)

#            print collectionSet

        if len(collectionSet) != articleCount:
            print 'The collection size differs from articleCount: ' + articleCount + '. The size is: ', len(collectionSet)

        diseaseArticleIDlist[disease]['PMIDs'].extend(list(collectionSet))

        if len(diseaseArticleIDlist[disease]['PMIDs']) != 500:
            print 'We did not succeed in getting the default number of records (500), however we did get ', len(diseaseArticleIDlist[disease]['PMIDs'])

        diseaseArticleIDlist[disease]['description'] = diseaseDictionary[disease]['desc']

        return diseaseArticleIDlist

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

def getArticleIDsFromMultiSource(database='', uid='', searchterm='', number_of_articles=20):

    if database.lower()=='pubmed':
        if number_of_articles==0: number_of_articles=getArticleCount(searchterm)
        
        handle=Entrez.esearch(db = database, term=searchterm, retmax=number_of_articles)
        results = Entrez.read(handle)
        ids = results['IdList']
    elif database.lower()=='omim' and uid != '':
        handle=Entrez.elink(db=database, LinkName='omim_pubmed_calculated', from_uid=uid)
        results = Entrez.read(handle)
        ids = [link['Id'] for lin in results[0]['LinkSetDb'][0]['Link']]
    
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
