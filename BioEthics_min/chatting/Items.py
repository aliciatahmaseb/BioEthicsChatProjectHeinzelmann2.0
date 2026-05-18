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
        
    * ranks statements by total pairwise distance across all players (lowest distance = most agreement overall)
    * picks the top (currently 3 but will be 12) 
    * randomly pick (now 2 will be 6) from these which will actually be discussed 
    * returns to the chatting app the selected_indices of the statements and the statments themselves 

"""
def get_top_statements(data_list, statements):
    data = np.array(data_list)
    num_players = data.shape[0]
    num_statements = data.shape[1]

    statement_distances = []

    # sum |a - b| across all pairs for statement r
    for r in range(num_statements):
        total = 0
        for i in range(num_players):
            for j in range(i + 1, num_players):
                total += abs(int(data[i, r]) - int(data[j, r]))
        statement_distances.append((r,total))
        # get for statement_distances: [(r = 0, total0), (r = 1, total1), (r = 2, total2), (r = 3, total3), (r = 4, total4)] - e.g., [(0, 193), (1, 88), (2, 145), (3, 210), (4, 67)]

    # sort by distance ascending
    # ???? key=lambda x: x[1] tells sorted — "when comparing elements to sort them, use the second element of each tuple as the sorting criterion."
    sorted_statements = sorted(statement_distances, key = lambda x : x[1])

    # we pick the first 12 (the lowest values)
    # top_12, still a list of tuples, looks like this: [(3, 12), (7, 18), (1, 24), ...]
    # top_12 = sorted_statements[:12]

    ### TEST - pick 3 of the 5
    top_3 = sorted_statements[:3]

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

