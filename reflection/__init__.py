from otree.api import *
import numpy as np

doc = """
Scenario: Reflection 

"""


class C(BaseConstants):
    NAME_IN_URL = 'reflection'
    PLAYERS_PER_GROUP = None
    STATEMENTS = ["A", "B", "C"]
    # so i get the statement valuations on different pages!
    NUM_STATEMENTS = len(STATEMENTS)
    NUM_ROUNDS = NUM_STATEMENTS
    NUM_PLAYERS = 4



class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):

    ### AFTER CHAT ###

    rating_post = models.IntegerField(min=0, max=101)
    confidence_post = models.IntegerField(min=0, max=101)


    # store one rating per round!:
    # construct a vector across rounds
    def get_ratings_array_post(self):
        return np.array([
            self.rating_post for p in self.in_all_rounds()],
            dtype =int)

    def get_confidence_array_post(self):
        return np.array([
            self.confidence_post for p in self.in_all_rounds()],
            dtype =int)


#PAGES

## To get the valuations of the players ##
class PostChatRating(Page):
    form_model = "player"
    form_fields = ["rating_post"]

    def vars_for_template(player: Player):
        print(f"Round {player.round_number} of {C.NUM_ROUNDS}")
        return dict(
            # in order to only get one of the statements not all at once
            statement = C.STATEMENTS[player.round_number - 1]
        )
class ConfidencePost(Page):
    # this is to collect the confidence level for each statement
    form_model = "player"
    form_fields = ["confidence_post"]

    def vars_for_template(player: Player):
        return dict(
            # in order to only get one of the statements not all at once
            statement = C.STATEMENTS[player.round_number - 1],
            rating_post=player.rating_post
        )

class StoreRatings(WaitPage):
    # store ratings globally per participant as participant.vars persists across apps
    # now we have cross-app storage
    def is_displayed(player):
        return player.round_number == C.NUM_ROUNDS
    @staticmethod
    def after_all_players_arrive(subsession: Subsession):
        for p in subsession.get_players():
            # reflecting is the key for the dictionary
            p.participant.vars['relecting'] = p.get_ratings_array_post()
class Instructions(Page):
    pass
class End(Page):
    def is_displayed(player):
        return player.round_number == C.NUM_ROUNDS

page_sequence = [Instructions,
                 PostChatRating,
                 ConfidencePost,
                 StoreRatings,
                 End
                 ]


