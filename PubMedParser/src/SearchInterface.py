import CosineMeasureOR
import CosineMeasureAND

def cosineMeasureOR(M_lil, M_csc, queryString):

    """
    Return the tuple with (pmidhash, angle in radians)
    """

    results = CosineMeasureOR.cosineMeasureOR(M_lil, M_csc, queryString)

    return results


def cosineMeasureAND(M_lil,M_csc,queryString):

    """
    Returns only rows that contain all the searched terms. In other words,
    there exists an implicit AND between each term in the query.
    """

    result = CosineMeasureAND.cosineMeasureAND(M_lil,M_csc,queryString)

    return result