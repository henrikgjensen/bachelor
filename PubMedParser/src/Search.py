#! /usr/bin/python

import SearchInterface
import SearchTermDoc

def search20(M_lil, M_csc, queryString):

    # Search-heuristic used to retrieve the list of results
    results=SearchInterface.cosineMeasureAND(M_lil, M_csc, queryString)

    # Sort the results
    results.sort()

    # Retrieve the top 20 results as PMIDs
    pmidList=SearchTermDoc.getPMIDList(results[0:19])

    return pmidList
