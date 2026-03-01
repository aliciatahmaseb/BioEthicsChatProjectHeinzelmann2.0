from otree.api import *
import numpy as np
from .matching import ilp_schedule
from gen_data_max.ChatWaitPage import Make_Chat_Wait_Page
from gen_data_max.ChatPage import Make_Chat_page

doc = """
explanation of what happens: this is for the maximisation 

* gather data of the participants 
* call the matching function 
* use the pairs from schedule to assign them to chats for the statements we want them to chat about 
* There will be around 5 chats 
"""


class C(BaseConstants):
    NAME_IN_URL = 'gen_data_max'
    PLAYERS_PER_GROUP = None
    STATEMENTS = ["A", "B", "C"]
    NUM_ROUNDS = 1
    NUM_PLAYERS = 14
    NUM_STATEMENTS = 3


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):

    ### BEFORE CHAT ###

    rating_pre_1 = models.IntegerField(min=0, max=101)
    rating_pre_2 = models.IntegerField(min=0, max=101)
    rating_pre_3 = models.IntegerField(min=0, max=101)

    ### AFTER CHAT ###

    rating_post_1 = models.IntegerField(min=0, max=101)
    rating_post_2 = models.IntegerField(min=0, max=101)
    rating_post_3 = models.IntegerField(min=0, max=101)

    # make sure each individual rating is stored in a matrix for the player:
    def get_ratings_array(self):
        return np.array([
            self.rating_pre_1,
            self.rating_pre_2,
            self.rating_pre_3
        ], dtype =int)

    @property
    def chat_nickname(self):
        # Show ID in subsession
        # this property allows for sending name in each chat bubble as their nickname
        # we want to make sure we see who is the player (but this is only for OWN interest -- needs to be removed)
        return f"Player{self.id_in_subsession}"

def compute_pairing(player_values: np.ndarray):

    data_max = player_values

    print("Input Data:")
    print(data_max)

    schedule = ilp_schedule(data_max)
    my_matrix_max = schedule

    print(my_matrix_max)

    print("\nGenerated Schedule:")
    for i, round in enumerate(schedule):
        print(f"Round {i + 1}:")
        print(round)
    return my_matrix_max #will be stored for later use

# PAGES

## To get the valuations of the players ##
class PreChatRating(Page):
    form_model = "player"
    form_fields = ["rating_pre_1", "rating_pre_2", "rating_pre_3"]

    def vars_for_template(player: Player):
        return dict(
            statements = C.STATEMENTS
        )

## To create the pairs ##

class ResultsWaitPage(WaitPage):
    wait_for_all_groups = True

    @staticmethod
    def after_all_players_arrive(subsession: Subsession):
        # via get_players I ask: give me all players in this app right now
        players = subsession.get_players()

        # create a matrix of all the players' p ratings for each statement (num_players x num_statements)
        # array (i.e., a row) is to store numbers in a grid (is a matrix instead of a python list)
        # np.vstack stacks the arrays into a 2D array (i.e., matrix)
        data_maximisation = np.vstack([p.get_ratings_array() for p in players])
        print("Data Matrix:", data_maximisation)

        #compute pairs (schedule) - what is returned when calling compute_pairing
        my_matrix_max = compute_pairing(data_maximisation)
        print("Computed Schedule:", my_matrix_max)

        # need to store the matrix!! - this is a list[list[tuple]]
        subsession.session.vars["my_matrix_max"] = my_matrix_max

## For the chatting ##

ChatWaitPageA = Make_Chat_Wait_Page(0, C.STATEMENTS[0])
ChatWaitPageB = Make_Chat_Wait_Page(1, C.STATEMENTS[1])
ChatWaitPageC = Make_Chat_Wait_Page(2, C.STATEMENTS[2])

ChatA = Make_Chat_page(0)
ChatB = Make_Chat_page(1)
ChatC = Make_Chat_page(2)



class Results(Page):
    pass

page_sequence = [PreChatRating,
                 ResultsWaitPage,
                 ChatWaitPageA,
                 ChatA,
                 ChatWaitPageB,
                 ChatB,
                 ChatWaitPageC,
                 ChatC
                 ]

#for round_index, statement in enumerate(C.STATEMENTS):
#    page_sequence.append(Make_Chat_Wait_Page(round_index, statement))
#    page_sequence.append(Make_Chat_page(round_index))


#page_sequence.append(Results)


