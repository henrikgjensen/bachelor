#! /usr/bin/python

import SearchInterface
import SearchTermDoc
import TextCleaner
import FilterInterface


# Set True for Porter-stemming
_stemmer=False


def search20(M_lil, M_csc, queryString):

    """
    
    """

    # OPTIONAL:
    # Stem the information
    if _stemmer: queryString=FilterInterface.porterStemmer(queryString)

    # CHOOSE HEURISTIC:
    # Search-heuristic used to retrieve the list of results
    results=SearchInterface.cosineMeasureAND(M_lil, M_csc, queryString)

    # Sort the results and reverse to get the highest score first
    (results.sort()).reverse()

    top20=[result[1] for result in results[0:19]]

    # Retrieve the top 20 results as PMIDs
    pmidList=SearchTermDoc.getPMIDList(top20)

    return pmidList
