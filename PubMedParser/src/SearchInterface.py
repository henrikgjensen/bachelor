import SearchAND

def searchAND(M_lil,M_csc,searchVector):

    """
    Returns only rows that contain all the searched terms. In other words,
    there exists an implicit AND between each term in the query.
    """

    result = SearchAND.searchAND(M_lil,M_csc,searchVector)

    return result


