from Bio import Entrez
from Bio import Medline


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
    This function takes search terms and an integer representing how many
    articles that should be searched for. A list of article-ids is returned.
    If no number is given, 20 articles will be returned. If 0 is given, all
    articles found will be returned.
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