import itertools
import numpy as np
import pulp

#this is a function to max, I can create one to minimise too
def ilp_schedule(data, maximize=True):
    """
    ILP solver for a maximum-weight multi-round pairing schedule.

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
    # .shape[0] gives us the number of rows in data --> gives us the number of players
    if data.shape[0] % 2 == 1:
        raise ValueError("An even number of participants is required")

    # .shape[1] gives us the number of columns --> this is our number of rounds
    R = data.shape[1]

    ### Generate the set of potential player pairs ###
    # by using range, we create integers from 0 till n-1 (so if data.shape[0] = 4 p = [0,1,2,3])
    P = list(range(data.shape[0]))
    # get all possible pairs (bcs of 2) without repeating pairs
    pairs = [(i, j) for i, j in itertools.combinations(P, 2)]

    ### Create the weights ###
    # create a numpy array which is some sort of matrix --> we get a multidimensional array. The shape is (len(p), len(p), R)
    # p is the number of participants so if this was 10, we get as shape, 10 x 10 x number of items R -- our (x,y,z) matrix -- which has double pairs
    weights = np.zeros(shape=(len(P), len(P), R))
    for i in range(len(P)):
        for j in range(len(P)):
            for r in range(R):
                weights[i,j,r] = abs(data[i,r] - data[j,r])

    ### Create Integer Linear Programming model ###
    # need to set maximise = False if want to have pulp.LpMinimize
    optimization_operation = pulp.LpMaximize if maximize else pulp.LpMinimize
    # call the model DiscussionScheduling and we pass optimization_operation
    # create optimisation problem (does nothing yet, just define it)
    model = pulp.LpProblem("DiscussionScheduling", optimization_operation)

    ### Decision variables ###
    # pulp.LpVariable(name, lowBound, upBound, category)
    # for every possible pair, for every possible round, create one binary variable (remains empty!)
    x = {
        (i, j, r): pulp.LpVariable(f"x_{i}_{j}_{r}", 0, 1, pulp.LpBinary)
        for (i, j) in pairs
        for r in range(R)
    }

    ### Objective: maximize total weight across all rounds ###
    # add to the problem the objective
    # sum of the product between the weight and the decision variables for each pair in each round
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
    # what happens: sent the objective and constraints to the solver
    # solver chooses values for all LpVariables --> now our x will get values (for i,j and r)
    # CBC --> default open-source solver PuLP uses
    # msg = false --> suppresses solver output (does not print solver message)
    model.solve(pulp.PULP_CBC_CMD(msg=False))

    ### Extract schedule ###
    # question : is this creating an empty list where that we have more colons not just one dimension?
    # does it allow us to have as elements lists (so lists in lists?)
    # create a list for each round so schedule is a list of lists (bcs we have multiple pairs per round)
    schedule = [[] for _ in range(R)]


    # x is our LpVariable, if it 0, the pair is not scheduled, if it is 1, it is scheduled
    # x.items --> returns ((i,j,r), LpVariable) --> (i, j, r), var --> (i, j, r) is the key, and var is the LpVariable object associated with key (either 1 or 0)
    # var (being 0 or 1) only becomes a value after model.solve
    # if the var.value is 1, the pair will we attached to the schedule in that round (so if solver chose x(i,j,r) = 1, then the pair (i,j) is scheduled in round r, and appended
    for (i, j, r), var in x.items():
        if var.value() > 0.5:
            schedule[r].append((i, j))

    return schedule