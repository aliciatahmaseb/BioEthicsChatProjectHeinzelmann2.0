from otree.api import *
import numpy as np
from .matching import ilp_schedule

doc = """
Minimisation experiment:
- Pre-chat ratings (agreement + confidence)
- Matching
- Chats per statement
"""

# ----------------------------------------------------------------
# CONSTANTS
# ----------------------------------------------------------------

class C(BaseConstants):
    NAME_IN_URL = 'gen_data_min'
    PLAYERS_PER_GROUP = None
    STATEMENTS = ["A", "B", "C"]
    NUM_STATEMENTS = 3
    NUM_ROUNDS = NUM_STATEMENTS
    NUM_PLAYERS = 14


# ----------------------------------------------------------------
# MODELS
# ----------------------------------------------------------------

class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):

    # BEFORE CHAT (per round)
    rating_pre = models.IntegerField(min=0, max=100)
    confidence_pre = models.IntegerField(min=0, max=100)

    # AFTER CHAT (kept as before)
    rating_post_1 = models.IntegerField(min=0, max=100)
    rating_post_2 = models.IntegerField(min=0, max=100)
    rating_post_3 = models.IntegerField(min=0, max=100)

    def get_ratings_array(self):
        """Collect pre-chat agreement ratings across rounds"""
        return np.array(
            [self.in_round(r).rating_pre for r in range(1, C.NUM_STATEMENTS + 1)],
            dtype=int
        )

    @property
    def chat_nickname(self):
        return f"Player{self.id_in_subsession}"


# ----------------------------------------------------------------
# MATCHING
# ----------------------------------------------------------------

def compute_pairing(player_values: np.ndarray):
    schedule = ilp_schedule(player_values)
    return schedule


# ----------------------------------------------------------------
# PAGES: PRE-CHAT (6 PAGES TOTAL)
# ----------------------------------------------------------------

class PreChatRating(Page):
    form_model = "player"
    form_fields = ["rating_pre"]

    @staticmethod
    def vars_for_template(player: Player):
        return dict(
            statement=C.STATEMENTS[player.round_number - 1],
            counter=player.round_number,
        )


#class PreChatConfidence(Page):
#    form_model = "player"
#    form_fields = ["confidence_pre"]

#    @staticmethod
#    def vars_for_template(player: Player):
#        return dict(
#            statement=C.STATEMENTS[player.round_number - 1],
#            counter=player.round_number,
#        )


# ----------------------------------------------------------------
# MATCHING WAIT PAGE
# ----------------------------------------------------------------

class ResultsWaitPage(WaitPage):
    wait_for_all_groups = True

    @staticmethod
    def is_displayed(player):
        return player.round_number == C.NUM_STATEMENTS

    @staticmethod
    def after_all_players_arrive(subsession: Subsession):
        players = subsession.get_players()
        data_minimisation = np.vstack([
            [p.in_round(r).rating_pre for r in range(1, C.NUM_STATEMENTS + 1)]
            for p in players
        ])
        subsession.session.vars["my_matrix_min"] = compute_pairing(data_minimisation)
#        data = np.vstack([p.get_ratings_array() for p in players])


# ----------------------------------------------------------------
# CHAT WAIT PAGES
# ----------------------------------------------------------------

class ChatWaitPageA(WaitPage):
    wait_for_all_groups = True

    @staticmethod
    def after_all_players_arrive(subsession: Subsession):
        players = subsession.get_players()
        pairs = subsession.session.vars["my_matrix_min"][0]
        subsession.set_group_matrix([[players[i], players[j]] for i, j in pairs])


class ChatWaitPageB(ChatWaitPageA):
    pass


class ChatWaitPageC(ChatWaitPageA):
    pass


# ----------------------------------------------------------------
# CHAT PAGES
# ----------------------------------------------------------------

class ChatA(Page):
    @staticmethod
    def vars_for_template(player: Player):
        return dict(
            statement=C.STATEMENTS[0],
            nickname=player.chat_nickname,
            channel=f"chat_A_group_{player.group.id_in_subsession}"
        )


class ChatB(Page):
    @staticmethod
    def vars_for_template(player: Player):
        return dict(
            statement=C.STATEMENTS[1],
            nickname=player.chat_nickname,
            channel=f"chat_B_group_{player.group.id_in_subsession}"
        )


class ChatC(Page):
    @staticmethod
    def vars_for_template(player: Player):
        return dict(
            statement=C.STATEMENTS[2],
            nickname=player.chat_nickname,
            channel=f"chat_C_group_{player.group.id_in_subsession}"
        )


# ----------------------------------------------------------------
# PAGE SEQUENCE
# ----------------------------------------------------------------

page_sequence = [
    PreChatRating,
#    PreChatConfidence,
    ResultsWaitPage,
    ChatWaitPageA, ChatA,
    ChatWaitPageB, ChatB,
    ChatWaitPageC, ChatC,
]
