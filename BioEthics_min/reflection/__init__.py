from otree.api import *
import numpy as np

doc = """
Scenario: Reflection 

"""


class C(BaseConstants):
    NAME_IN_URL = 'reflection'
    PLAYERS_PER_GROUP = None
    STATEMENTS = ["Die DNA von Verdächtigen mit DNA zu vergleichen, die an einem Tatort gefunden wurde, ist...",
                  "Von selbsterklärten Erben Gentests als Beweis der Abstammung zu verlangen ist ... ",
                  "An einem Embryo im Mutterleib Gentests durchzuführen, um das Risiko für Downsyndrom zu bestimmen, ist.."
                  ]
    # so i get the statement valuations on different pages!
    NUM_STATEMENTS = len(STATEMENTS)
    NUM_ROUNDS = NUM_STATEMENTS
    NUM_PLAYERS = 4



class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    age = models.IntegerField(label="Bitte geben Sie ihr Alter in Jahren an", min=18, max=100)
    gender = models.StringField(
        choices=["weiblich (einschließlich Transfrau)", "männlich (einschließlich Transmann)", "Nicht-binär", "Ich möchte diese Frage lieber nicht beantworten", "Sonstiges"],
        label= "Mit welchem Geschlecht identifizieren Sie sich?",
        widget=widgets.RadioSelect
    )
    gender_other  = models.StringField(
        label = "Bitte spezifizieren:",
        blank = True #damit man auch was weiss lassen darf - nur einfüllen bei andere
    )
    # sexuality = models.StringField(
    #     choices=["Homosexuell", "Heterosexuell", "Asexuell", "Bisexuell", "Sonstiges"],
    #     label="Wie würdest du deine sexuelle Orientierung beschreiben?",
    #     widget=widgets.RadioSelect
    # )
    Ethnicity = models.StringField(
        choices = ["Afrikanisch",
                   "Schwarz / Afroamerikanisch",
                   "Karibisch",
                   "Ostasiatisch",
                   "Lateinamerikanisch / Hispanoamerikanisch",
                   "Mittlerer Osten",
                   "Gemischt",
                   "Amerikanische*r Ureinwohner*in oder Ureinwohner*in Alaskas",
                   "Südasiatisch",
                   "Weiß / Kaukasisch",
                   "Weiß / Sephardische*r Jude / Jüdin",
                   "Schwarz / Britisch",
                   "Weiße*r Mexikaner*in",
                   "Sinti und Roma", "Südostasiatisch",
                   "Ich möchte diese Frage lieber nicht beantworten",
                   "Andere"],
        label = "Bitte geben Sie Ihre ethnische Zugehörigkeit an (d. h. die ethnische Zugehörigkeit von Menschen beschreibt ihr Gefühl der Zugehörigkeit und Verbundenheit mit einer bestimmten Gruppe einer größeren Bevölkerung, die ihre Abstammung, Hautfarbe, Sprache oder Religion teilt):",
        widget=widgets.RadioSelect
    )
    Ethnicity_other = models.StringField(
        label = "Bitte spezifizieren:",
        blank = True
    )

    Political_Orientation = models.StringField(
        choices=[
            "1", "2", "3", "4", "5",
            "6", "7", "8", "9", "10",
            "Ich möchte diese Frage lieber nicht beantworten"
        ],
        label="Bitte geben Sie Ihre politische Orientierung an (1 (extrem rechts),10 (extrem links))",
        widget=widgets.RadioSelect
    )

    Religion = models.StringField(
        choices=[
            "1", "2", "3", "4",
            "5", "6", "7",
            "Ich möchte diese Frage lieber nicht beantworten"
        ],
        label="Ich würde mich selbst als religiös beschreiben (1 (stimme gar nicht zu), 7 (stimme vollständig zu))",
        widget=widgets.RadioSelect
    )

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
class Instructions(Page):
    def is_displayed(player):
        # only shown in round 1
        return player.round_number == 1
## To get the valuations of the players ##
class PostChatRating(Page):
    form_model = "player"
    form_fields = ["rating_post"]

    def vars_for_template(player: Player):
        # TO CHECK IN WHICH ROUND WE ARE: print(f"Round {player.round_number} of {C.NUM_ROUNDS}")
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
    wait_for_all_groups = True
    def is_displayed(player):
        return player.round_number == C.NUM_ROUNDS
    @staticmethod
    def after_all_players_arrive(subsession: Subsession):
        for p in subsession.get_players():
            # reflecting is the key for the dictionary
            p.participant.vars['relecting'] = p.get_ratings_array_post()

class Demographics(Page):
    form_model = "player"
    form_fields = [
        'age',
        'gender',
        'gender_other',
        'Ethnicity',
        'Ethnicity_other',
        'Political_Orientation',
        'Religion']

    def is_displayed(
            player):  # Is only shown when the number of rounds = the last one, i.e., it only appears at the end:
        return player.round_number == C.NUM_ROUNDS



class End(Page):
    def is_displayed(player):
        return player.round_number == C.NUM_ROUNDS

page_sequence = [Instructions,
                 PostChatRating,
                 StoreRatings,
                 Demographics,
                 End
                 ]
