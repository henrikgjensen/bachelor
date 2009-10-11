def searchTermCombiner(listOfSearchTerms):

    # We might consider making this a class.

    """
    This modules is used to generate search terms to be used with the
    Pubmed[SearchEngine|Parser|Something], and different combinations
    of these. This is to help reduce the amount of returned
    articles. This is made seperately to be able to change the way it
    works more easily.
    """
    
    combinedSearchTermList = []

    # We need to get the last term containing all search terms,
    # stopping with len(lOST) results in one missing combination
    for i in range(1, len(listOfSearchTerms) + 1): 
        for uc in xuniqueCombinations(listOfSearchTerms, i):
            combinedSearchTermList.append(' '.join(uc))
        

    # Append 'AND hasabtract[text]' to each search term.
    return [term + ' AND hasabstract[text]' for term in combinedSearchTermList]
        
    # Might consider remove reversed searchterm, as Pubmed does not
    # distincguise these. E.g. Myostoma Cyst returns the same as Cyst
    # Myostoma (Or do they?) <-- These are fictious names.

# This is stolen code.
def xuniqueCombinations(items, n):
    if n==0: yield []
    else:
        for i in xrange(len(items)):
            for cc in xuniqueCombinations(items[i+1:],n-1):
                yield [items[i]]+cc
