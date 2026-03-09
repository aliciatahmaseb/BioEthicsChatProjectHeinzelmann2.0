from otree.api import *
import numpy as np
from .matching import ilp_schedule
from bioethics_max import C as ethics
from .ChatWaitPage import ChatWaitPage
from .ChatPage import Chat

# !!! COM: this is if we assume all statements are used. If not, what is in our case, we need to redefine statements in C and fill it with the correct statements we want to discuss
# statements = ethics.STATEMENTS.copy()


doc = """
This is for the pairing based on collected data in the bioethics_max app, and construct the chats for all rounds 
"""


class C(BaseConstants):
    NAME_IN_URL = 'chatting'
    PLAYERS_PER_GROUP = None
    # !!! COM: this must be adapted according to the statements we make use of
    # !!! COM: we say that statements x, y and z have to be discussed. Then the NUM_ROUNDS = 3
    STATEMENTS_CHAT = ["A", "B"]
    NUM_ROUNDS = len(STATEMENTS_CHAT)


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    @property
    def chat_nickname(self):
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
class MyPage(Page):
    pass

#import the statements
# i compute the pairing which is via the "compute_pairing" command - get the schedule
# my_matrix_max is the matrix we use for the chatting
class StartWaitPage(WaitPage):
    wait_for_all_groups = True

    @staticmethod
    def after_all_players_arrive(subsession: Subsession):

        # via get_players I ask: give me all players in this app right now
        players = subsession.get_players()

        # create a matrix of all the players' p ratings for each statement (num_players x num_statements)
        # array (i.e., a row) is to store numbers in a grid (is a matrix instead of a python list)
        # np.vstack stacks the arrays into a 2D array (i.e., matrix)

        # we stored the ratings of the players and now call them back via the key "valuation":
        data_maximisation = np.vstack([
            p.participant.vars["valuation"]
            for p in players
        ])

        print("Data Matrix:", data_maximisation)

        #compute pairs (schedule) - what is returned when calling compute_pairing

        my_matrix_max = compute_pairing(data_maximisation)

        print("Computed Schedule:", my_matrix_max)

        # need to store the matrix!! - this is a list[list[tuple]]

        subsession.session.vars["my_matrix_max"] = my_matrix_max


class Results(Page):
    pass


page_sequence = [StartWaitPage,
                 ChatWaitPage,
                 Chat]
