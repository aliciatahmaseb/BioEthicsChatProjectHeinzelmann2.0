from otree.api import *

class ChatWaitPage(WaitPage):
    #wait_for_all_groups = True

    @staticmethod
    def group_by_arrival_time_method(players):
        """
        Use the stored schedule to form groups for the current round.
        Each group is a pair from the schedule.
        """

        # players is a list of al waiting players
        # players[0] is a convention meaning "i need any player to reach this shared data" - I could also write players[24]
        # round_index is to make sure we get the correct round number (not sure what role it plays here)

        round_index = players[0].round_number - 1

        # my_matrix_min is our matrix with pairs -- get access to it via session.vars[...] -- it is just data (pairs of IDs) but oTree does not work with IDs; it needs actual Player objects grouped together
        # [[0,3],[1,2]] are just numbers, not usable groups
        # by using the round_index; we get the correct pairs for that round
        # pair_matrix_round: slice for the current round (it would give you all the pairs "for that specific round"), e.g., [[0,3],[1,2]]
        pair_matrix_round = players[0].session.vars["my_matrix_min"][round_index]

        groups = []

        # for each pair, find matching player object (get one group) -- as oTree works with groups, we need to create them
        # it coverts [[0,3],[1,2]] to [[player0, player3],[player1, player2]]
        for pair in pair_matrix_round:
            # group_players: filters the players list down to the two players whose IDs are in that pair and add to group
            # get p in players, see if its ID (of p) is in pair...
            # ... if yes, we add the two players in the pair (which we stored in group_players) to groups
            group_players = [
                # loop over all waiting players
                p for p in players
                # check if this player's ID is in the current pair
                # if the player's ID is in pair, they are included in group_players
                if (p.id_in_subsession - 1) in pair
            ]
            groups.append(group_players)

        return groups
