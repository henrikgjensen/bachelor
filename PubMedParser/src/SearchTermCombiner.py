def searchTermCombiner(listOfSearchTerms, additionalSearchOptions='', minimumToCombine=2):

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
    for i in range(minimumToCombine, len(listOfSearchTerms) + 1): 
        for uc in _xuniqueCombinations(listOfSearchTerms, i):
            combinedSearchTermList.append((i,' '.join(uc)+additionalSearchOptions))
        

    # Append 'AND hasabtract[text]' to each search term.
    return combinedSearchTermList#[term + additionalSearchOptions for term in combinedSearchTermList]
        
    # Might consider remove reversed searchterm, as Pubmed does not
    # distincguise these. E.g. Myostoma Cyst returns the same as Cyst
    # Myostoma (Or do they?) <-- These are fictious names.

# This is stolen code.
def _xuniqueCombinations(items, n):
    if n==0: yield []
    else:
        for i in xrange(len(items)):
            for cc in _xuniqueCombinations(items[i+1:],n-1):
                yield [items[i]]+cc
