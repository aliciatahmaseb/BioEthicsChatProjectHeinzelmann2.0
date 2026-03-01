from otree.api import *

def Make_Chat_page(round_index):
    class Custom_Chat(Page):
        template_name = "gen_data_max/Custom_Chat.html"
        #form_model = "player"
        #form_fields = ["chat_text"]


        @staticmethod
        def vars_for_template(player):
            round_index = player.round_number - 1
            STATEMENTS = ["A", "B", "C"]

            # get matrix from session for this round - get the first line for instance:
            #pair_matrix_round = player.subsession.session.vars["my_matrix_max"][round_index]

            # find the pair for this statement with the current player in:
            # as our matrix is a list of lists, the element of our matrix is a list of the lenght 2
                # in case that the list has the lenght 3, p would be [a,b,c], in case our matrix was a vector, p would be just A.
            # player.id_in_subsession - 1 bcs we want the index (player would be 1, but i the matrix, for player 1, we have index 0)
            # if (player.id_in_subsession - 1) in p --> checks if current player is in this pair p
            # next() --> returns the first pair where the above condition is true
            # All the players that should chat together in this group.
            #pair = next(p for p in pair_matrix_round if (player.id_in_subsession - 1) in p)

            # Get schedule for this round
            pair_matrix_round = player.subsession.session.vars["my_matrix_max"][round_index]

            # Find the pair for the current player
            pair = next(p for p in pair_matrix_round if (player.id_in_subsession - 1) in p)

            # Shared channel for both players
            channel = f"chat_statement_{round_index}_{pair[0]}_{pair[1]}"

            #channel = f"chat_statement_player_{player.id_in_subsession}"

            # return to the html page statements and nickname
            # both statements and nickname have been defined before
            # find STATEMENTS in class C, and find chat_nickname in class player
            return dict(
                statements= STATEMENTS[round_index],
                nickname = player.chat_nickname, #this is called so needs to be passed -- comes from class player
                participant_label=player.chat_nickname,
                channel = channel
            )

    Custom_Chat.__name__ = f"ChatPage_{round_index}"

    return Custom_Chat
