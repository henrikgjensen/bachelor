import TextCleaner

def calculateCorrelation(M,searchVector):


    # Convert the sparse amtrix to a compressed-sparse-row matrix
    M=M.todok()

    # Sanitize the search vector and convert it to a list of terms
    sanitizer=TextCleaner.sanitizeString()
    searchVector=[term.lower() for term in sanitizer.sub(' ', searchVector).split(' ') if term!='']

    print str(searchVector)


    for pmid in range(M.shape[0]-1):

        vector=M[pmid+1,1:]

        print pmid
