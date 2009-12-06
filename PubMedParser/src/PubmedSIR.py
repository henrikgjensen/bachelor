from Bio import Entrez
from Bio import Medline
import SearchTermCombiner as STC
reload(STC)
import TextCleaner as TC
reload(TC)
import DiseaseCrawler as DC
reload(DC)
import math
import IOmodule
reload(IOmodule)
import os
from time import sleep

mainFolder = 'The_Hive'
subFolder = 'data_acquisition'

# Path to main folder
_path=os.getenv("HOME")
_path+='/'+_path+'/'+mainFolder+'/'+subFolder

# If mainFolder and subFolder do not exists, create it.
if not os.path.isdir(_path):
    os.mkdir(_path)

# Collector function that gathers all functionality.
def gatherOfAllThings(startIndex=0,stopIndex=None, dataSourceDir=str(_path)+"/rarediseases_info"):

    # Get the number of diseases from DC, based on start and stop. If
    # stopIndex = None, then it returns the whole range
    numberOfRareDiseases = len(DC.readDiseases(startIndex,stopIndex))
    # Default number per chuck, before writeout
    numberToGet = 1
    # Calculate the numbers of steps, for looping.
    steps = int(math.ceil(numberOfRareDiseases / numberToGet))

    # Default directory to save information files in.
    directory = 'medline_records'
    _path_medlinerecords+=_path+'/'+directory
    if not os.path.isDir(_path_medlinerecords):
        os.mkdir(_path_medlinerecords)

    # Read in the range of diseases we want to get information about,
    # in a list, it needs to be sorted to support resume.
    d=DC.readDiseases(startIndex,stopIndex)

    for i in range(steps):
        # Read in the a chuck of diseases in a list
        diseaseList = d[i * numberToGet:i * numberToGet + numberToGet]

        diseaseDictionary = {}

        for i in range(len(diseaseList)):
            # Transfer the ordered disease list into an unordered
            # dictionary
            diseaseDictionary[diseaseList[i].keys()[0]] = diseaseList[i].values()[0]

        dictionary = {}
        # Runs through the disease dictionary and gets all the PMIDs
        # for each disease
        diseaseDictionary = getArticleIDs(diseaseDictionary)

        for disease in diseaseDictionary:

            dictionary[disease] = {}
            dictionary[disease]['records']=[]
            dictionary[disease]['description'] = diseaseDictionary[disease]['description']

            dictionary[disease]['records'].extend(getMedlineList(diseaseDictionary[disease]['PMIDs']))

            IOmodule.writeOutTxt(_path_medlinerecords, disease, dictionary[disease], 'w')

def getArticleIDs(diseaseDictionary):

    """
    Takes a dictionary of the form:
    {'disease xx': {'syn' : [xx, yy], 'term' : string, 'uid' : string,
    'description' : string }, etc}}

    And returns a dictionary containing:
    {'disease a': [pmid1, pmid2, pmid3...], 'disease b' : [pmidx,
    pmidy,...], ...}

    Where disease xx is the name of the disease, syn is a list of
    synonyms, term is a hand crafted search term (if it exists),
    description is the description from the rarediseases.info (if it
    exists).

    Duplicate PMIDs are removed.
    """

    # Iterates through the diseaseDictionary and searches for uid,
    # term, diseasename, and combinations of synonyms
    diseaseArticleIDlist={}
    # Contains additional options, e.g. ' AND LA[eng]'
    additionalSearchOptions = ' AND hasabstract[text]'

    for disease in diseaseDictionary:

        print
        print 'Processing:', disease
        articleCount=250
        diseaseArticleIDlist[disease] = {}
        diseaseArticleIDlist[disease]['PMIDs']=[]
        diseaseArticleIDlist[disease]['description'] = ''
        # Either the disease has a handcrafted search string or it contains either pubmed or omim uid.
        if (diseaseDictionary[disease]['terms'] != ''):
            diseaseArticleIDlist[disease]['PMIDs'].extend(getArticleIDsFromMultiSource(diseaseDictionary[disease]['db'],'',TC.unquoteString(diseaseDictionary[disease]['terms']) + additionalSearchOptions,articleCount))
        elif (diseaseDictionary[disease]['uid'] != ''):
            diseaseArticleIDlist[disease]['PMIDs'].extend(getArticleIDsFromMultiSource(diseaseDictionary[disease]['db'],diseaseDictionary[disease]['uid'],'',articleCount))
        articleCount = articleCount - len(diseaseArticleIDlist[disease]['PMIDs'])

        # If we still have qouta left, make a search on the disease name
        if (articleCount > 0):
            # Sanitize the disease name string for searching and append the additional search option.
            # diseaseName = ' '.join([part.lower().strip() for part in disease.split(' ') if part != ''])
            # Search for the disease name on pubmed/medline
            diseaseArticleIDlist[disease]['PMIDs'].extend(getArticleIDsFromMultiSource(database='pubmed',uid='',searchterm=disease + additionalSearchOptions,numberOfArticles=articleCount))

        # Remove duplicates
        diseaseArticleIDlist[disease]['PMIDs'] = removeDuplicates(diseaseArticleIDlist[disease]['PMIDs'])

        # diseaseArticleIDlist, should contain about 250 PMIDs by now,
        # but we have a max limit on 500 records, therefore we wish to
        # fill up with the other search form now. (By searching on
        # synonyms)
        articleCount = 500 - len(diseaseArticleIDlist[disease]['PMIDs'])

        # Translate the special signs contained in some synonyms
        diseaseDictionary[disease]['syn']=[TC.decodeURLcharacters(TC.unquoteString(i)).encode('utf-8','ignore') for i in diseaseDictionary[disease]['syn']]

        # Create a set of all combinations of synonyms and save it in
        # 'optimizedSynonymList'
        synonymArticleIDlist={}
        optimizedSynonymList = sorted(STC.searchTermCombiner(diseaseDictionary[disease]['syn'], additionalSearchOptions,1))

        # Go though the list of synonyms, download corresponding PMIDs
        # from Pubmed and delete synonyms not returned any PMIDs (and
        # all combinations containing this synonym!).  Note that the
        # sorted nature of the the list of tuples in
        # 'optimizedSynonymList' allows us to delete post-indices
        # while iterating through it without getting indexs errors or
        # missing any steps.
        print "================================================"
        print "Total number of synonyms:",len(optimizedSynonymList)
        printcount=len(optimizedSynonymList)
        for synTuple in optimizedSynonymList:
            synonym=synTuple[1]
            print "Gathering data from: \""+synonym+"\""
            synonymArticleIDlist[synonym]=[]

            # We don't need to get more medline records than can be
            # crammed into the 500 - primary search, so we use the
            # articleCount as paramter. Hopefully there will be lots
            # of small results that get used up first.
            synonymArticleIDlist[synonym].extend(getArticleIDsFromMultiSource('pubmed', '', synonym, articleCount))
            if len(synonymArticleIDlist[synonym])==0:
                tempList=optimizedSynonymList[:]
                for syn in tempList:
                    shortenedSyn=synonym[0:(len(synonym)-len(additionalSearchOptions))]
                    if (synonym != syn[1]) and (shortenedSyn in syn[1]):
                        print "Deleted: "+str(syn)
                        optimizedSynonymList.remove(syn)
                        printcount-=1
                    if (synonym == syn[1]):
                        printcount-=1
                print "-------",printcount,"remaining -------"
            else:
                print "Done with "+str(synTuple)
                printcount-=1
                print "-------",printcount,"remaining -------"
        print "================================================"

        print 'Sorting items accoring to their count by values()'
        # Needs to get the list sorted on the amount of return IDs.
        items = [(len(v),v,k) for k,v in synonymArticleIDlist.items()]
        # Sort according to the length of the lists withing the tuples
        items.sort()
        # Reverse to get largest to smallest in list
        items.reverse()

        listIsEmpty = False

        # Gonna make a list of maximum 250 PMIDs from the synonym
        # list, without duplicates. As set contains unordered, unique
        # elements, we use a set to collect the PMIDs
        collectionSet = set()

        # We might consider changing this, because right now, we check
        # twice to see whether collectionSet exceeds articleCount
        while len(collectionSet) <= articleCount or not listIsEmpty:

            # Is the list of items empty, then we can't do anything.
            if items == []:
                listIfEmpty = True
                break

            transferTuple = items.pop()

            if transferTuple[0] == 0:
                continue

            for pmid in transferTuple[1]:
                # Test to see if len of the set is articleCount?
                if (len(collectionSet) + articleCount) > 499:
                    break
                collectionSet.add(pmid)

        # Print some useful information about the number of returned
        # articles from each of the search types
        print 'Hand crafted / Disease name search returned:', str(len(diseaseArticleIDlist[disease]['PMIDs'])), 'results'
        print 'Synonym search returned:', str(len(collectionSet)), 'results'
        print 'Total number of results:', str(len(collectionSet) + len(diseaseArticleIDlist[disease]['PMIDs']))

        diseaseArticleIDlist[disease]['PMIDs'].extend(list(collectionSet))

        # This might be unusable information, might consider removing it.
        if len(diseaseArticleIDlist[disease]['PMIDs']) == 0:
            print 'The disease:', disease + ' did not return any results.'
        elif len(diseaseArticleIDlist[disease]['PMIDs']) != 500:
            print 'We did not succeed in getting the default number of records (500), however we did get ', len(diseaseArticleIDlist[disease]['PMIDs'])
        
        # Copy over the disease description, if none is present, the
        # value will be empty string ''
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

def getArticleIDsFromMultiSource(database='', uid='', searchterm='', numberOfArticles=20):

    ###########################################################
    ### WE NEED TO SEARCH ON THE DISEASE NAME IF PUBMED UID ###
    ### OR OMIM UID DO NOT RETURN 250 MEDLINE RECORDS!!!    ###
    ### THIS NEEDS TO BE ADDED IN THE getArticleID func.    ###
    ###########################################################    

    """
    This function is for getting PMIDs from different sources. The are
    a number of different sources available. We first see if the
    database is PUBMED and if the uid is set. In this case we need to
    use Entrez.elink for performing our search. If uid is not set we
    need to use Entrez.esearch instead.

    If the database is OMIM then we need to use Entrez.elink to
    perform the search

    """

    # Number of retries per disease, high due to unstable
    # internetconnection.
    numberOfRetries = 100
    # Sleep time between retries, default 5 sec
    sleepTimeBetweenTries = 5

    if database.lower()=='pubmed':
        if uid != '':
            for i in range(numberOfRetries):
                try:
                    handle=Entrez.elink(db=database, from_uid=uid)
                    break
                except:
                    print 'Could not get article count for:', searchterm
                    print 'Retrying...', str(i+1),'out of ' + str(numberOfRetries)
                    sleep(sleepTimeBetweenTries)
            results = Entrez.read(handle)
            ids = [link['Id'] for link in results[0]['LinkSetDb'][0]['Link']][:numberOfArticles]
        else:
            for i in range(numberOfRetries):
                try:
                    if numberOfArticles==0: numberOfArticles=getArticleCount(searchterm)
                    break
                except:
                    print 'Could not get article count for:', searchterm
                    print 'Retrying...', str(i+1),'out of ' + str(numberOfRetries)
                    sleep(sleepTimeBetweenTries)
            for i in range(numberOfRetries):
                try:
                    handle=Entrez.esearch(db = database, term=searchterm, retmax=numberOfArticles)
                    break
                except:
                    print 'Could not get article count for:', searchterm
                    print 'Retrying...', str(i+1),'out of ' + str(numberOfRetries)
                    sleep(sleepTimeBetweenTries)
            results = Entrez.read(handle)
            ids = list(results['IdList'])[:numberOfArticles]
    elif database.lower()=='omim' and uid != '':
        for i in range(numberOfRetries):
            try:
                handle=Entrez.elink(db=database, LinkName='omim_pubmed_calculated', from_uid=uid)
                break
            except:
                print 'Could not get article count for:', searchterm
                print 'Retrying...', str(i+1),'out of ' + str(numberOfRetries)
                sleep(sleepTimeBetweenTries)
        results = Entrez.read(handle)
        ids = [link['Id'] for link in results[0]['LinkSetDb'][0]['Link']][:numberOfArticles]

    # else:
    #    implement emergency search on disease name

    
    return ids

def getArticleCount(search_term):

    """
    This function takes search terms and returns the total number of
    found articles in the PubMed database.
    """

    Entrez.email = 'henrikgjensen@gmail.com'
    
    for i in range(100):
        try: 
            handle=Entrez.esearch(db='pubmed',term=search_term,retmax='0')
            break
        except:
            print 'Failed to get article count for:', search_term
            print 'Retrying...', str(i+1),'out of 100'
    record=Entrez.read(handle)
    retmax_length=record['Count']
    print 'Counted a total of',retmax_length,'articles'
    return retmax_length

def getMedlineList(pmids):

    """
    This function takes a list of article-ids and returns a list of
    MedLine articles that contains an abstract.
    """

    records = []
    cleaned_records = []
    listLength = len(pmids)

    Entrez.email = 'henrikgjensen@gmail.com'

    for i in range(0, listLength, 650):
        tempList = pmids[i:i + 650]
        handle = Entrez.efetch(db='pubmed', id=tempList,rettype='medline', retmode='text')
        try:
            records.extend(list(Medline.parse(handle)))
        except:
            IOmodule.writeOutTxt(_path+'/'+'errordir_medline_records', pmids[i], '')

        print 'Downloaded',len(records),'MedLine articles.',str(listLength-len(records)),'remaining...'

    for article in records:
        if 'AB' in article:
            cleaned_records.append(article)
    
    print 'Returned',len(cleaned_records),'MedLine articles containing an abstract.'
    return cleaned_records
