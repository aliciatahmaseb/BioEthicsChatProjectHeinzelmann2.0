from otree.api import *
from .Items import STATEMENTS_CHAT

#PROBLEM HERE:
# I do not choose the statement that I want to have discussed
# I just take the one out of STATEMENTS with the index rounds_number - 1

class Chat(Page):
    template_name = "Custom_Chat.html"

    @staticmethod
    def vars_for_template(player):

        # !! round index automatically selects the correct statement and pairing.
        round_index = player.round_number - 1

        statement = STATEMENTS_CHAT[round_index]

        # get schedule for this round
        pair_matrix_round = player.session.vars["my_matrix_max"][round_index]

        # find this player's pair
        pair = next(
            p for p in pair_matrix_round
            if (player.id_in_subsession - 1) in p
        )

        #shared channel for both players
        channel = f"chat_statement_{round_index}_{pair[0]}_{pair[1]}"

        return dict(
            statement= statement,
            nickname=player.chat_nickname,
            participant_label=player.chat_nickname,
            channel=channel
        )
