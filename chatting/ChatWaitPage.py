from otree.api import *

class ChatWaitPage(WaitPage):
    wait_for_all_groups = True

    @staticmethod
    def group_by_arrival_time_method(players):
        """
        Use the stored schedule to form groups for the current round.
        Each group is a pair from the schedule.
        """

        round_index = players[0].round_number - 1

        pair_matrix_round = players[0].session.vars["my_matrix_max"][round_index]

        groups = []
        for pair in pair_matrix_round:
            group_players = [
                p for p in players
                if (p.id_in_subsession - 1) in pair
            ]
            groups.append(group_players)

        return groups