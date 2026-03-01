import itertools
import numpy as np
import pulp

#this is a function to max, I can create one to minimise too
def ilp_schedule(data, maximize = False):
    """
    ILP solver for a minimum-weight multi-round pairing schedule.

    Parameters
    ----------
    data : np.array
        The response data by the participants, which is used to calculate
        the weights. Expected shape is (NUMBER_OF_PLAYERS, NUMBER_OF_ROUNDS).
    maximize: bool
        Whether ot not we are maximizing or minimizing the weights. Set to
        True to have different opinions scheduled together.

    Returns
    -------
    schedule : list[list[tuple]]
        The returned list contains an entry per round. Each entry is a list in
        itself that contains tuples for all pairs. - for each round we have a list of pairs
    """

    ### Assert that an even number of participants is given.###
    if data.shape[0] % 2 == 1:
        raise ValueError("An even number of participants is required")

    R = data.shape[1]

    ### Generate the set of potential player pairs ###

    P = list(range(data.shape[0]))
    # get all possible pairs (bcs of 2) without repeating pairs
    pairs = [(i, j) for i, j in itertools.combinations(P, 2)]

    ### Create the weights ###

    weights = np.zeros(shape=(len(P), len(P), R))
    for i in range(len(P)):
        for j in range(len(P)):
            for r in range(R):
                weights[i,j,r] = abs(data[i,r] - data[j,r])

    ### Create Integer Linear Programming model ###
    # need to set maximise = False if want to have pulp.LpMinimize
    optimization_operation = pulp.LpMaximize if maximize else pulp.LpMinimize

    model = pulp.LpProblem("DiscussionScheduling", optimization_operation)

    ### Decision variables ###

    x = {
        (i, j, r): pulp.LpVariable(f"x_{i}_{j}_{r}", 0, 1, pulp.LpBinary)
        for (i, j) in pairs
        for r in range(R)
    }

    ### Objective: minimise total weight across all rounds ###

    model += pulp.lpSum(weights[i, j, r] * x[(i, j, r)] for (i, j) in pairs for r in range(R))

    ### Constraint 1: each player plays at most once per round ###
    for r in range(R):
        for i in P:
            model += pulp.lpSum(
                x[(min(i, j), max(i, j), r)]
                for j in P if j != i
                if (min(i, j), max(i, j)) in pairs
            ) == 1

    ### Constraint 2: each pair can occur at most once ###
    for (i, j) in pairs:
        model += pulp.lpSum(x[(i, j, r)] for r in range(R)) <= 1

    ### Solve the ILP ###

    model.solve(pulp.PULP_CBC_CMD(msg=False))

    ### Extract schedule ###

    schedule = [[] for _ in range(R)]



    for (i, j, r), var in x.items():
        if var.value() > 0.5:
            schedule[r].append((i, j))

    return schedule