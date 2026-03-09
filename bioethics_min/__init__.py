from otree.api import *
import numpy as np

doc = """
Scenario: Minimisation 

this is to gather the valuation for the statements before the chat 
"""


class C(BaseConstants):
    NAME_IN_URL = 'gen_data_min'
    PLAYERS_PER_GROUP = None
    TESTROUND = "Probe"
    # !!! COM: should be adapted with the correct statements
    STATEMENTS = ["Die DNA von Verdächtigen mit DNA zu vergleichen, die an einem Tatort gefunden wurde, ist...",
                  "Von selbsterklärten Erben Gentests als Beweis der Abstammung zu verlangen ist ... ",
                  "An einem Embryo im Mutterleib Gentests durchzuführen, um das Risiko für Downsyndrom zu bestimmen, ist.."
                  ]
    # !!! COM: so i get the statement valuations on different pages! - this will be 18 if we make it ready for our experiment
    NUM_STATEMENTS = len(STATEMENTS)
    NUM_ROUNDS = NUM_STATEMENTS
    NUM_PLAYERS = 14



class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):

    ### BEFORE CHAT ###
    test = models.IntegerField(min=0, max=101)
    rating_pre = models.IntegerField(min=0, max=101)
    confidence = models.IntegerField(min=0, max=101)

    # store one rating per round!:
    # construct a vector across rounds
    def get_ratings_array_pre(self):
        return np.array([
            self.rating_pre for p in self.in_all_rounds()],
            dtype =int)

    def get_confidence_array(self):
        return np.array([
            self.confidence for p in self.in_all_rounds()],
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

class Confidence(Page):
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


page_sequence = [StartIntro,
                 Instructions,
                 TestPage,
                 Start,
                 PreChatRating,
                 Confidence,
                 StoreRatings
                 ]


