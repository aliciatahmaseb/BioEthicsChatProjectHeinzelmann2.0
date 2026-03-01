from otree.api import *
import numpy as np
from .matching import ilp_schedule
from gen_data_min.ChatWaitPage import Make_Chat_Wait_Page
#from gen_data_min.ChatPage import Make_Chat_page

doc = """
explanation of what happens: this is for the minimisation 

* gather data of the participants 
* call the matching function 
* use the pairs from schedule to assign them to chats for the statements we want them to chat about 
* There will be around 5 chats 
"""


class C(BaseConstants):
    NAME_IN_URL = 'gen_data_min'
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

    data_min = player_values

    print("Input Data:")
    print(data_min)

    schedule = ilp_schedule(data_min)
    my_matrix_min = schedule

    print(my_matrix_min)

    print("\nGenerated Schedule:")
    for i, round in enumerate(schedule):
        print(f"Round {i + 1}:")
        print(round)
    return my_matrix_min #will be stored for later use

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
        data_minimisation = np.vstack([p.get_ratings_array() for p in players])
        print("Data Matrix:", data_minimisation)

        #compute pairs (schedule) - what is returned when calling compute_pairing
        my_matrix_min = compute_pairing(data_minimisation)
        print("Computed Schedule:", my_matrix_min)

        # need to store the matrix!! - this is a list[list[tuple]]
        subsession.session.vars["my_matrix_min"] = my_matrix_min

class ChatWaitPageA(WaitPage):
    wait_for_all_groups = True

    @staticmethod
    def after_all_players_arrive(subsession: Subsession):
        players = subsession.get_players()
        schedule = subsession.session.vars["my_matrix_min"]

        round_pairs = schedule[0]  # A

        group_matrix = []
        for i, j in round_pairs:
            group_matrix.append([
                players[i],   # index → Player object
                players[j]
            ])

        subsession.set_group_matrix(group_matrix)

        print("\n=== Groups for Statement A ===")
        for g in subsession.get_groups():
            print([p.id_in_subsession for p in g.get_players()])

class ChatWaitPageB(WaitPage):
    wait_for_all_groups = True

    @staticmethod
    def after_all_players_arrive(subsession: Subsession):
        players = subsession.get_players()
        schedule = subsession.session.vars["my_matrix_min"]

        round_pairs = schedule[1]  # A

        group_matrix = []
        for i, j in round_pairs:
            group_matrix.append([
                players[i],   # index → Player object
                players[j]
            ])

        subsession.set_group_matrix(group_matrix)

        print("\n=== Groups for Statement B ===")
        for g in subsession.get_groups():
            print([p.id_in_subsession for p in g.get_players()])
class ChatWaitPageC(WaitPage):
    wait_for_all_groups = True

    @staticmethod
    def after_all_players_arrive(subsession: Subsession):
        players = subsession.get_players()
        schedule = subsession.session.vars["my_matrix_min"]

        round_pairs = schedule[2]  # A

        group_matrix = []
        for i, j in round_pairs:
            group_matrix.append([
                players[i],   # index → Player object
                players[j]
            ])

        subsession.set_group_matrix(group_matrix)

        print("\n=== Groups for Statement C ===")
        for g in subsession.get_groups():
            print([p.id_in_subsession for p in g.get_players()])

class ChatA(Page):
    @staticmethod
    def vars_for_template(player: Player):

        # return to the html page statements and nickname
        # both statements and nickname have been defined before
        # find STATEMENTS in class C, and find chat_nickname in class player
        return dict(
            statements=C.STATEMENTS[0],
            nickname = player.chat_nickname,
            participant_label=player.chat_nickname,
            channel=f"chat_statement_A_group_{player.group.id_in_subsession}"
        )

class ChatB(Page):
    @staticmethod
    def vars_for_template(player: Player):
        return dict(
            statements=C.STATEMENTS[1],
            nickname=player.chat_nickname,
            participant_label=player.chat_nickname,
            channel=f"chat_statement_B_group_{player.group.id_in_subsession}"
        )

class ChatC(Page):
    @staticmethod
    def vars_for_template(player: Player):
        return dict(
            statements=C.STATEMENTS[2],
            nickname=player.chat_nickname,
            participant_label=player.chat_nickname,
            channel = f"chat_statement_C_group_{player.group.id_in_subsession}" #create unique identifier for each chat room
            # chat_statement_C_Group -> indicate that the chat corresponds to statement B
            # Ex - chat_statement_B_Group_3 if the players are in
        )

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



