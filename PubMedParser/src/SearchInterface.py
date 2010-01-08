import CosineMeasure
import SumMeasure

def cosineMeasure(M_lil, M_csc, queryString):

    """
    Calculates the square-root of cosine measures.

    Returns a list of tuples on the form:
    [(angle in radians, pmidhash1),(angle in radians, pmidhash2),...]
    """

    results = CosineMeasure.cosineMeasure(M_lil, M_csc, queryString)

    return results


def sumMeasure(M_lil,M_csc,queryString):

    """
    Returns only rows that contain all the searched terms. In other words,
    there exists an implicit AND between each term in the query.
    """

    results = SumMeasure.sumMeasure(M_lil,M_csc,queryString)

    return results
