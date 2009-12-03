import SearchAND
import CosineMeasure

def searchAND(M_lil,M_csc,searchString):

    """
    Returns only rows that contain all the searched terms. In other words,
    there exists an implicit AND between each term in the query.
    """

    result = SearchAND.searchAND(M_lil,M_csc,searchString)

    return result


def cosineMeasure(M_lil, M_csc, searchString):

    """
    Return the tuple with (pmidhash, angle in radians)
    """

    results = CosineMeasure.cosineMeasure(M_lil, M_csc, searchString)

    return results
