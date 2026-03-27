from otree.api import *
import numpy as np

doc = """
Scenario: Maximisation 

this is to gather the valuation for the statements before the chat 
"""


class C(BaseConstants):
    NAME_IN_URL = 'gen_data_max'
    PLAYERS_PER_GROUP = None
    TESTROUND = "Probe"
    # !!! COM: should be adapted with the correct statements
    STATEMENTS = ["A", "B", "C"]
    # !!! COM: so i get the statement valuations on different pages! - this will be 18 if we make it ready for our experiment
    NUM_STATEMENTS = len(STATEMENTS)
    # change according to the number of rounds that we envision
    NUM_ROUNDS = NUM_STATEMENTS
    NUM_PLAYERS = 14



class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):

    ### BEFORE CHAT ###
    test= models.IntegerField(min=0, max=101)
    rating_pre = models.IntegerField(min=0, max=101)
    confidence = models.IntegerField(min=0, max=101)


    # store one rating per round!:
    # construct a vector across rounds
    def get_ratings_array_pre(self):
        return np.array([
            p.rating_pre for p in self.in_all_rounds()],
            dtype =int)

    def get_confidence_array(self):
        return np.array([
            p.confidence for p in self.in_all_rounds()],
            dtype =int)


# PAGES
class Introduction(Page):
    def is_displayed(player):
        #only shown in round 1
        return player.round_number == 1

class Instructions(Page):
    def is_displayed(player):
        return player.round_number == 1

class TestPage(Page):
    form_model = "player"
    form_fields = ["test"]

    def vars_for_template(player: Player):
        return dict(
            # in order to only get one of the statements not all at once
            testing=C.TESTROUND[player.round_number - 1]
        )

class TestWaitPage(WaitPage):
    wait_for_all_groups = True
    def is_displayed(player):
        # only shown in round 1
        return player.round_number == 1
    @staticmethod
    def after_all_players_arrive(subsession):
        import random
        testplayers = subsession.get_players()

        # to make sure the pairing is random
        random.shuffle(testplayers)

        # matrix in which the test pairs are stored
        test_matrix = []

        # fill in the matrix with pairs
        for i in range(0, len(testplayers), 2):
            pair = [testplayers[i], testplayers[i+1]]
            test_matrix.append(pair)

        # as they are no longer players, but now groups of two, need to use subsession
        # what does set_group_matrix stand for again
        subsession.set_group_matrix(test_matrix)

class TestChat(Page):
    def is_displayed(player):
        # only shown in round 1
        return player.round_number == 1

class StartIntro(Page):
    def is_displayed(player):
        # only shown in round 1
        return player.round_number == 1

## To get the valuations of the players ##
class PreChatRating(Page):
    form_model = "player"
    form_fields = ["rating_pre"]

    def vars_for_template(player: Player):
        return dict(
            # in order to only get one of the statements not all at once
            statement = C.STATEMENTS[player.round_number - 1]
        )

class confidence(Page):
    # this is to collect the confidence level for each statement
    form_model = "player"
    form_fields = ["confidence"]

    def vars_for_template(player: Player):
        return dict(
            # in order to only get one of the statements not all at once
            statement = C.STATEMENTS[player.round_number - 1],
            rating_pre=player.rating_pre
        )

class StoreRatings(WaitPage):
    wait_for_all_groups = True
    # store ratings globally per participant as participant.vars persists across apps
    # now we have cross-app storage

    def is_displayed(player):
        return player.round_number == C.NUM_ROUNDS

    @staticmethod
    def after_all_players_arrive(subsession: Subsession):
        for p in subsession.get_players():
            # valuation is the key for the dictionary
            p.participant.vars['valuation'] = p.get_ratings_array_pre()

class Start(WaitPage):
    wait_for_all_groups = True
    def is_displayed(player):
        # only shown in round 1
        return player.round_number == 1

page_sequence = [#StartIntro,
                 #Instructions,
                 #TestPage,
                 #TestWaitPage,
                 #TestChat,
                 #Start,
                 PreChatRating,
                 confidence,
                 StoreRatings
                 ]


