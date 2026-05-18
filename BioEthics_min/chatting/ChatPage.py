from otree.api import *
#from .Items import STATEMENTS_CHAT
from .Items import get_top_statements
from bioethics_min import C as ethics

doc = """ 

#COMMENT: I think this is wrong -- we do not need round_number, we just need to go through 
top_indices[round_index] -- like: for r in top_indices ... pick that statement and the pairs in my_matrix_min (so the correct row) 

 * uses round_number to pick which statement is discussed in this round 
 * uses top_indices[round_index] to look up the correct row in my_matrix_min 
 * get the pairs within that row, and construct a channel name unique so both players share the same room
 
 
 #COMMENT: these need some further explanation: 
 
 round_index = player.round_number - 1
 schedule_round_index = top_indices[round_index] 
 statement = top_statements[round_index]
 pair_matrix_round = my_matrix_min[schedule_round_index]
 pair = next(
     p for p in pair_matrix_round
     if (player.id_in_subsession - 1) in p)
     

     
     """
class Chat(Page):
    template_name = "Custom_Chat.html"


    ### COMMENTS: ###
    # from StartWaitPage in init_chatting:
    #
    # * we have "my_matrix_min", "top_indices" and "top_statements" stored via player.session.vars and can call them via their key which we store in variables we name the same as their key:
    # * top_indices: the original positions of the selected statements (e.g., if we select 2 of the 6 statements, we would get [0,2] which implies that the statements at position 0 and 2 were selected)
    # * top_statements: the list f selected statements

    @staticmethod
    def vars_for_template(player):
        my_matrix_min = player.session.vars["my_matrix_min"]
        top_indices = player.session.vars["top_indices"]
        top_statements = player.session.vars["top_statements"]

        # # round_index: which chat round is this? (0-based)
        # walks through top_indices one entry per round (as we have NUM_ROUNDS = 2, the player goes through the chat page twice (and round index makes sure it is in the form of (0,1) so we pick the correct indices out of the seelcted_indices)
        round_index = player.round_number - 1

        # REMOVE pass the above so we get the correct row from my_matrix_min
        # schedule_round_index = top_indices[round_index]

        statement_index = top_indices[round_index]
        print(statement_index)

        # if I am in round 2, I will get round_index = 1, and get the statement at position 1 out of top_statements, passed on to statement
        statement = top_statements[round_index]
        print(statement)

        # I CHANGED THIS, LOOK IF THE THING BELOW WORkS OR NOT
        # my_matrix_min is the full pairing schedule for all statements
        # by calling schedule_round_index, it pulls out the relevant row (i.e., relevant statement to be discussed from top_statements)
        # pair_matrix_round = my_matrix_min[schedule_round_index]

        # the pairs for this statement, converted to plain Python ints
        # (numpy integers can cause silent failures in 'in' checks)
        # my_matrix_min = list of rows where each row corresponds to one statement with pairs
        # --> my_matrix_min[statement_index] pulls out the row that is relevant (list of pairs for the current statement)
        # used to get rid of the numpy integers and get clean python lists
        # essentially, according to claude: It takes the row of pairs for the current statement and sanitizes all numpy integers into plain Python integers
        pair_matrix_round = [
            tuple(int(x) for x in p) # <- covert each element into one pair (goes from numpy integer (e.g., np.int64(0)) to python int and get them back into a tuple)
            for p in my_matrix_min[statement_index] # <- iterates over each pair p in that row
        ]

        # find this player's pair (0-based index) - convert player's id to match matrix's indexing system
        player_idx = int(player.id_in_subsession) - 1

        # loop through all pairs in the round and check if player's index is in that pair
        # stops at the first match and returns it (continues until found the correct partner and then jumps to the next)
        # ex: 0 goes through 0-p (or until there is a partner) then jump to the
       # pair = next(
       #     (p for p in pair_matrix_round if player_idx in p)
       # )

        found_pair = None
        for p in pair_matrix_round:
            # check if this player's index appears in the current pair
            if player_idx in p:
                found_pair = p
                break  # stop as soon as we find the match

        pair = found_pair


        # find this player's pair
        # loop through all pairs in the round and stops at the one that contains the current player's ID
        #pair = next(
        #    (p for p in pair_matrix_round
        #    if (player.id_in_subsession - 1) in p),
        #    None
        #)

        # shared channel for both players in pair: creates a unique chat room IC for each pair (e.g., chat_statement_0_0_3 if players 0 and 3 are paired in round 1)
        channel = f"chat_statement_{statement_index}_{pair[0]}_{pair[1]}"

        return dict(
            statement= statement,
            nickname=player.chat_nickname,
            participant_label=player.chat_nickname,
            channel=channel
        )

