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

# Collector function that gathers all functionality.
def gatherOfAllThings(startIndex=0,stopIndex=None):

    numberOfRareDiseases = len(DC.readDiseases(startIndex,stopIndex)) # Get the total number of diseases from DC.
    numberToGet = 5 # Default number per chuck, before writeout
    steps = int(math.ceil(numberOfRareDiseases / numberToGet))

    # Default directory to save information files in.
    directory = 'diseaseInformation'

    d=DC.readDiseases(startIndex,stopIndex)

    for i in range(steps):
        diseaseList = d[i * numberToGet:i * numberToGet + numberToGet]

        diseaseDictionary = {}

        for i in range(len(diseaseList)):
#            print diseaseList[i].keys(), diseaseList[i].values()
            diseaseDictionary[diseaseList[i].keys()[0]] = diseaseList[i].values()[0]

            
#        print diseaseDictionary
        
    # Calls the DiseaseCrawler to get all the diseases from it.
    # diseaseDictionary = DC.readDiseases()

    # Calls the module itself to get 500 PMIDs for each disease. Might
    # want to segment it the download to better be able to handle
    # crashes and such, but its only a proto type.

        dictionary = {}
        diseaseDictionary = getArticleIDs(diseaseDictionary)

        print 'Completed dictionary construction for iteration', str(i)
        print 'We still need to complete', str(numberOfRareDiseases - (i*numberToGet))
    
        for disease in diseaseDictionary:

            dictionary[disease] = {}
            dictionary[disease]['records']=[]
            dictionary[disease]['decription'] = diseaseDictionary[disease]['description']

            dictionary[disease]['records'].extend(getMedlineList(dictionary[disease]['PMIDs']))

            IOmodule.writeOut(directory, disease, dictionary[disease], 'w')
        
#            print 'test'
#            filepath=path+disease+'.txt'
#            outputFile = open(filepath,'w')
#            outputFile.write('Description:' + dictionary[disease]['description'])
#            print 'We should have written the Description to the file now:'
            # records = [line + '\n' for line in records] # Do not know whether this works or not.
#            for i in range(len(records)):
#                string = '{'
#                string = ''
#                for key in records[i]:
#                    string+=key+' : '+records[i][key]
#                    
#                outputFile.write(string)
            
#            outputFile.close()
                

def getArticleIDs(diseaseDictionary):

    """
    Takes a dictionary of the form:
    {'disease xx': {'terms' : [xx, yy], 'uid' : string, 'description' : string }, etc}
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
    additionalSearchOptions = ' AND hasabstract[text]' # Contains additional options, e.g. ' AND LA[eng]'

    for disease in diseaseDictionary:

        print
        print 'Processing:', disease
        articleCount=250
        diseaseArticleIDlist[disease] = {}
        diseaseArticleIDlist[disease]['PMIDs']=[]
        diseaseArticleIDlist[disease]['description'] = ''
        if (diseaseDictionary[disease]['terms'] != ''):
            diseaseArticleIDlist[disease]['PMIDs'].extend(getArticleIDsFromMultiSource(diseaseDictionary[disease]['db'],'',TC.unquoteString(diseaseDictionary[disease]['terms']) + additionalSearchOptions,articleCount))
        elif (diseaseDictionary[disease]['uid'] != ''):
            diseaseArticleIDlist[disease]['PMIDs'].extend(getArticleIDsFromMultiSource(diseaseDictionary[disease]['db'],diseaseDictionary[disease]['uid'],'',articleCount))

        articleCount = articleCount - len(diseaseArticleIDlist[disease]['PMIDs'])

        # If we still have qouta left
        if (articleCount > 0):
            # Search for the disease name on pubmed/medline
            diseaseArticleIDlist[disease]['PMIDs'].extend(getArticleIDsFromMultiSource('pubmed','',disease + additionalSearchOptions,articleCount))

        # Remove duplicates
        diseaseArticleIDlist[disease]['PMIDs'] = removeDuplicates(diseaseArticleIDlist[disease]['PMIDs'])

        # diseaseArticleIDlist, should contain about 250 PMIDs by now,
        # but we have a max limit on 500 articles, therefore we wish
        # to fill up with the other search form now. (By searching on
        # synonyms)
        articleCount = 500 - len(diseaseArticleIDlist[disease]['PMIDs'])

        # Call SearchTermCombiner to combine search terms and adds hasabstract[text] behind it.
        diseaseDictionary[disease]['syn'] = STC.searchTermCombiner(diseaseDictionary[disease]['syn'], additionalSearchOptions)

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
            print 'The collection size differs from articleCount: ' + str(articleCount) + '. The size is: ', len(collectionSet)

        diseaseArticleIDlist[disease]['PMIDs'].extend(list(collectionSet))

        if len(diseaseArticleIDlist[disease]['PMIDs']) == 0:
            print 'The disease:', disease + ' did not return any results.'
        elif len(diseaseArticleIDlist[disease]['PMIDs']) != 500:
            print 'We did not succeed in getting the default number of records (500), however we did get ', len(diseaseArticleIDlist[disease]['PMIDs'])
        

        diseaseArticleIDlist[disease]['description'] = diseaseDictionary[disease]['desc']

        # We have 500 diseases perform a write out of the PMIDs, and the description
        # if len(diseaseArticleIDlist) == 100:
        #     for disease in diseaseArticleIDlist:
        #         writeOut('diseasePMIDs',disease,diseaseArticleIDlist[disease])

        #     print 'Write out of 100 disease is completed. Flushing dictionary'
#        diseaseArticleIDlist = {}

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

        # for i in range(3):
        #     try:
        #         c=urllib2.urlopen(page)
        #     except:
        #         print "Could not open %s" % page
        #         print "Attempt",str(i+1),"out of 3"
        #         sleep(5)
        #         if i==2:
        #             print "Could not open page. Terminating.."
        #             raise StopIteration()


    if database.lower()=='pubmed':
        if uid != '':
            for i in range(3):
                try:
                    handle=Entrez.elink(db=database, from_uid=uid)
                except:
                    print 'Could not get article count for:', searchterm
                    print 'Retrying...', str(i+1),'out of 3'
                    sleep(5)
            results = Entrez.read(handle)
            ids = [link['Id'] for link in results[0]['LinkSetDb'][0]['Link']]
        else:
            for i in range(3):
                try:
                    if numberOfArticles==0: numberOfArticles=getArticleCount(searchterm)
                except:
                    print 'Could not get article count for:', searchterm
                    print 'Retrying...', str(i+1),'out of 3'
                    sleep(5)
            for i in range(3):
                try:
                    handle=Entrez.esearch(db = database, term=searchterm, retmax=numberOfArticles)
                except:
                    print 'Could not get article count for:', searchterm
                    print 'Retrying...', str(i+1),'out of 3'
                    sleep(5)
            results = Entrez.read(handle)
            ids = results['IdList']
    elif database.lower()=='omim' and uid != '':
        for i in range(3):
            try:
                handle=Entrez.elink(db=database, LinkName='omim_pubmed_calculated', from_uid=uid)
            except:
                print 'Could not get article count for:', searchterm
                print 'Retrying...', str(i+1),'out of 3'
                sleep(5)
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
