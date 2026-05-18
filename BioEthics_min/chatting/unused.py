import numpy as np
from bioethics_min import C as ethics
import random
from .matching import ilp_schedule
doc = """
To get the items discussed 

    From all statements, select the 12 where paired players
    agree most closely (overall distance in value assigned is smallest), then randomly pick 6 of those to discuss.

    Parameters
    ----------
    data_list : list
       -> The ratings matrix as a plain Python list (num_players x num_statements)
    statements : list
       -> The full list of statement strings

    Returns
    -------
    top_statements : list
        The 6 randomly selected statements to discuss
    top_indices : list
        Their indices in the original statements list

"""
def get_top_statements(data_list, statements):
    data = np.array(data_list)

    # run the ilp_schedule to get both schedule (i.e., pairs) and values (i.e., each individual in the pair's value (a (i,j) vector)- not yet distance)
    schedule, values = ilp_schedule(data, maximize = False)

    statement_distances = []

    # for each statement r (looking at the values), sum |a - b| across all pairs
    for r in range(len(values)):
        total_distance = sum(abs(i - j) for (i,j) in values[r])
        statement_distances.append((r, total_distance))

    # sort by distance ascending
    # ???? key=lambda x: x[1] tells sorted — "when comparing elements to sort them, use the second element of each tuple as the sorting criterion."
    sorted_statements = sorted(statement_distances, key = lambda x : x[1])

    # we pick the first 12 (the lowest values)
    # top_12, still a list of tuples, looks like this: [(3, 12), (7, 18), (1, 24), ...]
    # top_12 = sorted_statements[:12]

    ### TEST - pick 3 of the 5
    top_3 = sorted_statements[:2]

    # only keep the statement indices (r gets the statement index, dist gets the distance (the sum |a - b|), so here we throw away dist and keep indice): [3, 7, 1, ...]
    # top_12_indices = [r for r, dist in top_12]

    ### TEST
    top_3_indices = [r for r, dist in top_3]

    # randomly pick 6 of the 12 - takes the form [3, 7, 1, 2, 9, 17]:
    #selected_indices = random.sample(top_12_indices, 6)
    #selected_statements = [statements[r] for r in selected_indices]

    ### TEST
    selected_indices = random.sample(top_3_indices, 2)
    selected_statements = [statements[r] for r in selected_indices]


    return selected_statements, selected_indices

