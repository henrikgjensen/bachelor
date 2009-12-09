import CosineMeasureOR
import CosineMeasureAND

def cosineMeasureOR(M_lil, M_csc, queryString):

    """
    Returns a list of tuples on the form:
    [(angle in radians, pmidhash1),(angle in radians, pmidhash2),...]
    """

    results = CosineMeasureOR.cosineMeasureOR(M_lil, M_csc, queryString)

    return results


def cosineMeasureAND(M_lil,M_csc,queryString):

    """
    Returns only rows that contain all the searched terms. In other words,
    there exists an implicit AND between each term in the query.
    """

    results = CosineMeasureAND.cosineMeasureAND(M_lil,M_csc,queryString)

    return results