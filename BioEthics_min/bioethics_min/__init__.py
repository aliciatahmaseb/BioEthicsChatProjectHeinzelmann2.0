from otree.api import *
import numpy as np

doc = """
Scenario: Minimisation

this is to gather the valuation for the statements before the chat

It collects rating_pre and confidence_pre from each player for each statement across the different rounds 
At the end, StoreRatings assembles each player's ratings into a numpty array and saves it to 
participant.vars['valuation']

We can than access the ratings via p.vars['valuation'] and transfer the value to a new variable elsewhere

for instance in app chatting, we make use of: 

data_minimisation=  np.vstack([
            p.participant.vars["valuation"] for p in players
        ])
"""


class C(BaseConstants):
    NAME_IN_URL = 'gen_data_min'
    PLAYERS_PER_GROUP = None
    TESTROUND = "Probe"
    # !!! COM: should be adapted with the correct statements
    STATEMENTS = ["Die DNA von Verdächtigen mit DNA zu vergleichen, die an einem Tatort gefunden wurde, ist...",
                  "Von selbsterklärten Erben Gentests als Beweis der Abstammung zu verlangen ist ... ",
                  "An einem Embryo im Mutterleib Gentests durchzuführen, um das Risiko für Downsyndrom zu bestimmen, ist..",
                  "A",
                  "B",
                  #"C"
                  ]
    # !!! COM: so i get the statement valuations on different pages! - this will be 18 if we make it ready for our experiment
    NUM_STATEMENTS = len(STATEMENTS)
    NUM_ROUNDS = NUM_STATEMENTS
    # irrelevant as we set PLAYERS_PER_GROUP = 2 (what is in settings matters)
    NUM_PLAYERS = 12



class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):

    """ create arrays for confidence level and agreement level to the statement where the value of each round is stored """

    ### BEFORE CHAT ###
    test = models.IntegerField(min=0, max=101)
    rating_pre = models.IntegerField(min=0, max=101)
    confidence_pre = models.IntegerField(min=0, max=101)

    # store one rating per round!:
    # construct a vector across rounds
    def get_ratings_array_pre(self):
        return np.array([
            p.rating_pre for p in self.in_all_rounds()],
            dtype =int)

    def get_confidence_array(self):
        return np.array([
            p.confidence_pre for p in self.in_all_rounds()],
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
            # testing=C.TESTROUND[player.round_number - 1]
            testing = "Sich aus Spaß gegenseitig mit Essen in der Mensa zu bewerfen ist…"
        )

    def is_displayed(player):
        # only shown in round 1
        return player.round_number == 1

class TestWaitPage(WaitPage):
    wait_for_all_groups = True
    title_text = "Sobald die anderen Versuchspersonen die Testphasen abgeschlossen haben; beginnt das Experiment"
    body_text = "Warten auf die anderen Teilnehmer."
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

#class StartIntro(Page):
#    def is_displayed(player):
#        # only shown in round 1
#        return player.round_number == 1

class Start(WaitPage):
    wait_for_all_groups = True
    title_text = "Bitte warten"
    body_text = "Warten auf die anderen Teilnehmer..."

    def is_displayed(player):
        # only shown in round 1
        return player.round_number == 1

## To get the valuations of the players ##
class PreChatRating(Page):

    """ get the values before chat """

    form_model = "player"
    form_fields = ["rating_pre", "confidence_pre"]

    def vars_for_template(player: Player):
        return dict(
            # in order to only get one of the statements not all at once
            statement = C.STATEMENTS[player.round_number - 1]
        )

#class Confidence(Page):
#
#    """ get the confidence level before chat """
#
#    # this is to collect the confidence level for each statement
#    form_model = "player"
#    form_fields = ["confidence"]
#
#    def vars_for_template(player: Player):
#        return dict(
#            # in order to only get one of the statements not all at once
#            statement = C.STATEMENTS[player.round_number - 1],
#            rating_pre=player.rating_pre
#        )


class StoreRatings(WaitPage):

    """ make sure that all players are done and that the data is saved somewhere so we can access it in the next apps
    (stored into a format (i.e., array) that can be accesses in the next part of the experiment (other apps)
    """

    # wait until all the players in the entire session arrived
    wait_for_all_groups = True
    title_text = "Bitte warten"
    body_text = "Warten auf die anderen Teilnehmer..."
    # store ratings globally per participant as participant.vars persists across apps
    # now we have cross-app storage

    def is_displayed(player):
        # only shown in the last round
        return player.round_number == C.NUM_ROUNDS
    @staticmethod
    def after_all_players_arrive(subsession: Subsession):
        # go through all the players p (use get_players)
        for p in subsession.get_players():
            # save the results into participant.vars['valuation'] -> a dictionary that can get called upon across apps (available for later even if we go to another app)
            # valuation is the key for the dictionary
            # get_ratings_array_pre is the vector where we stored all the values the participants gave in each round, now we store this vector (or array) for each participant
            p.participant.vars['valuation'] = p.get_ratings_array_pre()


page_sequence = [Instructions,
                 TestWaitPage,
                 TestChat,
                 Start,
                 PreChatRating,
                 #Confidence,
                 StoreRatings
                 ]


