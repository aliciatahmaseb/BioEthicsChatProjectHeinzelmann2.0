from otree.api import *
import numpy as np
from .matching import ilp_schedule
from bioethics_min import C as ethics
from .ChatWaitPage import ChatWaitPage
from .ChatPage import Chat
from .Items import get_top_statements



doc = """
This is for the pairing based on collected data in the bioethics_min app, and construct the chats for all rounds 

I need to import the statements from the bioethics_min app 

In the "compute_pairing" command, I get the matrix of the pairs for all statements, which is calculated via the ilp_schedule function (in matching.py) - is returned when I call this command

my_matrix_max is returned and used in ChatPage.py to determine the chat pairs

StartWaitPage 
* waits for all players, then stacks everyone's rating arrays into a matrix (rows are the players and the columns are the statements) 
--> aka: data_minimisation (this matrix will be transfered to the function compute_pairing to compute the pairs (which itself calls the function in matching page (i.e., ilp_schedule)) 
* calls compute_pairing which itself calls ilp_schedule to find optimal pairs that mlin the difference in ratings (similar views) 
* ilp_schedule returns schedule which is saved as my_matrix_min to the StartWaitPage 
* also calls get_top_statement() from Items.py to get the statements that will be discussed in the chat by passing data_minimisation.tolist() and ethics.STATEMENTS
* we save them so we can use them globally: 
        subsession.session.vars["top_statements"] = top_statements
        subsession.session.vars["top_indices"] = top_indices


##COMMENT: I could maybe create another python page that I can get the function compute_pairing in so i can make use of it in other cases (beyond this algo)

"""


class C(BaseConstants):
    NAME_IN_URL = 'chatting'
    PLAYERS_PER_GROUP = None
    # !!! COM: this must be adapted according to the statements we make use of
    # !!! COM: we say that statements x, y and z have to be discussed. Then the NUM_ROUNDS = 3
    STATEMENTS_CHAT = list(ethics.STATEMENTS)
    #STATEMENTS_CHAT = ["Die DNA von Verdächtigen mit DNA zu vergleichen, die an einem Tatort gefunden wurde, ist...",
    #              "Von selbsterklärten Erben Gentests als Beweis der Abstammung zu verlangen ist ..."]
    # number bei uns wird 6
    NUM_ROUNDS = 2


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    @property
    def chat_nickname(self):
            return f"Player{self.id_in_subsession}"

# until now, this is printed in the consol for each chat - need to reduce it to one chat, maybe say: for round = 0
def compute_pairing(player_values: np.ndarray):

    data_min = player_values
    # get data_min printed in terminal
    print("Input Data:")
    print(data_min)

    # I call the function "ilp_schedule" which is in matching.py and store it in "schedule" qnd in values (the pairs and the values of the participants in each pair)

    schedule, values = ilp_schedule(data_min)

    # give the two returned matrices another name: my_matrix_min and my_matrix_values - not really necessary I think

    my_matrix_min = schedule
    my_matrix_values = values

    print(my_matrix_min)
    print(my_matrix_values)

    # to check if there are any bugs

    print("\nGenerated Schedule:")

    # for each item in schedule, give me its position i and its content round
    for i, round in enumerate(schedule):
        # get e.g., Round 1
        print(f"Round {i + 1}:")
        # print the pairs for that round
        print(round)
        # print the corresponding values for that round (a weird format: eg :[(np.int64(34), np.int64(14)), (np.int64(83), np.int64(14))])
        print(values[i])
        # get the values of each participant in each pair, and their distance between the two (can check if there is really a small difference)
        for (a,b) in values[i]:
            print(f" a= {a}, b={b}, difference = {abs(a-b)}")

    # will be stored for later use, can access it via subsession.session.vars
    # we do not return my_matrix_values -- WHYYYYY?????
    return my_matrix_min


# PAGES
class MyPage(Page):
    pass
class StartWaitPage(WaitPage):

    """ create a matrix of all the players' p ratings for each statement (num_players x num_statements) """

    wait_for_all_groups = True

    @staticmethod
    def after_all_players_arrive(subsession: Subsession):

        # to make sure that we only do this for the first round
        if subsession.round_number != 1:
            return

        # via get_players I ask: give me all players in this app right now
        players = subsession.get_players()
        # we stored the ratings of all the players and now call them back via the key "valuation" - we had the values stored in the dictionary participant.vars['valuation'] - by using valuation, we get the ratings
        # Essentially, with p.participant.vars["valuation"] for p in players we collect the player's ratings array into a python list of arrays and stack them on one another as rows)
        # by calling it and storing it in data_minimisation
        # np.vstack just means, we stack the vectors on each other (one row under another) - np.hstack means we have new columns (one next to the other)
        # each row is a player and each column is a statement """

        data_minimisation=  np.vstack([
            p.participant.vars["valuation"] for p in players
        ])

        # for checking:
        print("Data Matrix:", data_minimisation)

        # compute pairs (schedule) - what is returned when calling compute_pairing
        # we had created the command "compute_pairing" which makes use of "ilp_schedule" to return the matrix "my_matrix_min" which has all the optimal pairs
        # now we call it and store the matrix in my_matrix_min (as it was before)

        my_matrix_min = compute_pairing(data_minimisation)

        print("Computed Schedule:", my_matrix_min)

        # need to store the matrix!! - this is a list[list[tuple]]
        # we store the matrix with the key "my_matrix_min" so we have access to it in other apps too
        subsession.session.vars["my_matrix_min"] = my_matrix_min

        # store original ratings matrix too -- for passing it to the function in Items.py (see line below)
        subsession.session.vars["ratings_matrix"] = data_minimisation.tolist()

        # "get_top_statements" is imported from Items.py - get the top statements and top indices
        # we pass on data_minimisation.tolist() ( our ratings matrix which we calculated above) and ethics.STATEMENTS (our statements)
        # these two will be important in the ChatPage.py (see below)
        top_statements, top_indices = get_top_statements(data_minimisation.tolist(), ethics.STATEMENTS)

        # These two lines are important to be able to call them in ChatPage (we have stored top_statements and top_indices in a dictionary where the key is the same as their name)
        subsession.session.vars["top_statements"] = top_statements
        subsession.session.vars["top_indices"] = top_indices

class Results(Page):
    pass


page_sequence = [StartWaitPage,
                 ChatWaitPage,
                 Chat]
