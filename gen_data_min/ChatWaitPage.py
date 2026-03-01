from otree.api import *


doc = """
to do: i need to make sure i get the data from the schedule part which is not clear here yet
"""

# i need to pass the round (which is an integer) and the statement (which is a string)
def Make_Chat_Wait_Page(round_index: int, label : str ):
    class CustomChatWaitPage(WaitPage):
        # make sure all players arrive
        wait_for_all_groups = True

        @staticmethod
        def group_by_arrival_time_method(players):
            """
            Use the computed schedule to form temporary groups for this round.
            Each group is a pair from the schedule.
            """
            pair_matrix_round = players[0].subsession.session.vars["my_matrix_min"][round_index]

            groups = []
            for pair in pair_matrix_round:
                group_players = [p for p in players if (p.id_in_subsession - 1) in pair]
                groups.append(group_players)
            return groups

    return CustomChatWaitPage