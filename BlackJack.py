import sys
from random import shuffle

import numpy as np
import scipy.stats as stats
import pylab as pl
import matplotlib.pyplot as plt

from importer.StrategyImporter import StrategyImporter

SHOE_SIZE = 6
SHOE_PENETRATION = 0.25
BET_SPREAD = 19.0

DECK_SIZE = 52.0
CARDS = {"Ace": 11, "Two": 2, "Three": 3, "Four": 4, "Five": 5, "Six": 6, "Seven": 7, "Eight": 8, "Nine": 9, "Ten": 10, "Jack": 10, "Queen": 10, "King": 10}
BASIC_OMEGA_II = {"Ace": 0, "Two": 1, "Three": 1, "Four": 2, "Five": 2, "Six": 2, "Seven": 1, "Eight": 0, "Nine": -1, "Ten": -2, "Jack": -2, "Queen": -2, "King": -2}

BLACKJACK_RULES = {
    'triple7': False,  # Count 3x7 as a blackjack
}

HARD_STRATEGY = {}
SOFT_STRATEGY = {}
PAIR_STRATEGY = {}


class Card(object):
    """
    Represents a playing card with name and value.
    """
    def __init__(self, name, value):
        self.name = name
        self.value = value

    def __str__(self):
        return "%s" % self.name


class Shoe(object):
    """
    Represents the shoe, which consists of a number of card decks.
    """
    reshuffle = False

    def __init__(self, decks):
        self.count = 0
        self.count_history = []
        self.ideal_count = {}
        self.decks = decks
        self.cards = self.init_cards()
        self.init_count()

    def __str__(self):
        s = ""
        for c in self.cards:
            s += "%s\n" % c
        return s

    def init_cards(self):
        """
        Initialize the shoe with shuffled playing cards and set count to zero.
        """
        self.count = 0
        self.count_history.append(self.count)

        cards = []
        for d in range(self.decks):
            for c in CARDS:
                for i in range(0, 4):
                    cards.append(Card(c, CARDS[c]))
        shuffle(cards)
        return cards

    def init_count(self):
        """
        Keep track of the number of occurrences for each card in the shoe in the course over the game. ideal_count
        is a dictionary containing (card name - number of occurrences in shoe) pairs
        """
        for card in CARDS:
            self.ideal_count[card] = 4 * SHOE_SIZE

    def deal(self):
        """
        Returns:    The next card off the shoe. If the shoe penetration is reached,
                    the shoe gets reshuffled.
        """
        if self.shoe_penetration() < SHOE_PENETRATION:
            self.reshuffle = True
        card = self.cards.pop()

        assert self.ideal_count[card.name] > 0, "Either a cheater or a bug!"
        self.ideal_count[card.name] -= 1

        self.do_count(card)
        return card

    def do_count(self, card):
        """
        Add the dealt card to current count.
        """
        self.count += BASIC_OMEGA_II[card.name]
        self.count_history.append(self.truecount())

    def truecount(self):
        """
        Returns: The current true count.
        """
	# if db: print self.count / (self.decks * self.shoe_penetration()) 
        return self.count / (self.decks * self.shoe_penetration())

    def shoe_penetration(self):
        """
        Returns: Ratio of cards that are still in the shoe to all initial cards.
        """
        return len(self.cards) / (DECK_SIZE * self.decks)


class Hand(object):
    """
    Represents a hand, either from the dealer or from the player
    """
    _value = 0
    _aces = []
    _aces_soft = 0
    splithand = False
    surrender = False
    doubled = False

    def __init__(self, cards):
        self.cards = cards

    def __str__(self):
        h = ""
        for c in self.cards:
            h += "%s " % c
        return h

    @property
    def value(self):
        """
        Returns: The current value of the hand (aces are either counted as 1 or 11).
        """
        self._value = 0
        for c in self.cards:
            self._value += c.value

        if self._value > 21 and self.aces_soft > 0:
            for ace in self.aces:
                if ace.value == 11:
                    self._value -= 10
                    ace.value = 1
                    if self._value <= 21:
                        break

        return self._value

    @property
    def aces(self):
        """
        Returns: The all aces in the current hand.
        """
        self._aces = []
        for c in self.cards:
            if c.name == "Ace":
                self._aces.append(c)
        return self._aces

    @property
    def aces_soft(self):
        """
        Returns: The number of aces valued as 11
        """
        self._aces_soft = 0
        for ace in self.aces:
            if ace.value == 11:
                self._aces_soft += 1
        return self._aces_soft

    def soft(self):
        """
        Determines whether the current hand is soft (soft means that it consists of aces valued at 11).
        """
        if self.aces_soft > 0:
            return True
        else:
            return False

    def splitable(self):
        """
        Determines if the current hand can be splitted.
        """
        if self.length() == 2 and self.cards[0].name == self.cards[1].name:
            return True
        else:
            return False

    def blackjack(self):
        """
        Check a hand for a blackjack, taking the defined BLACKJACK_RULES into account.
        """
        if not self.splithand and self.value == 21:
            if all(c.value == 7 for c in self.cards) and BLACKJACK_RULES['triple7']:
                return True
            elif self.length() == 2:
                return True
            else:
                return False
        else:
            return False

    def busted(self):
        """
        Checks if the hand is busted.
        """
        if self.value > 21:
            return True
        else:
            return False

    def add_card(self, card):
        """
        Add a card to the current hand.
        """
        self.cards.append(card)

    def split(self):
        """
        Split the current hand.
        Returns: The new hand created from the split.
        """
        self.splithand = True
        c = self.cards.pop()
        new_hand = Hand([c])
        new_hand.splithand = True
        return new_hand

    def length(self):
        """
        Returns: The number of cards in the current hand.
        """
        return len(self.cards)


class Player(object):
    """
    Represent a player
    """
    def __init__(self, hand=None, dealer_hand=None):
        self.hands = [hand]
        self.dealer_hand = dealer_hand

    def set_hands(self, new_hand, new_dealer_hand):
        self.hands = [new_hand]
        self.dealer_hand = new_dealer_hand

    def play(self, shoe):
        for hand in self.hands:
            if db: print "Playing Hand: %s" % hand
            self.play_hand(hand, shoe)

    def play_hand(self, hand, shoe):
        if hand.length() < 2:
            if hand.cards[0].name == "Ace":
                hand.cards[0].value = 11
            self.hit(hand, shoe)

        while not hand.busted() and not hand.blackjack():
            if hand.soft():
                flag = SOFT_STRATEGY[hand.value][self.dealer_hand.cards[0].name]
            elif hand.splitable():
                flag = PAIR_STRATEGY[hand.value][self.dealer_hand.cards[0].name]
            else:
                flag = HARD_STRATEGY[hand.value][self.dealer_hand.cards[0].name]

            if flag == 'D':
                if hand.length() == 2:
                    if db: print "Double Down"
                    hand.doubled = True
                    self.hit(hand, shoe)
                    break
                else:
                    flag = 'H'

            if flag == 'Sr':
                if hand.length() == 2:
                    if db: print "Surrender"
                    hand.surrender = True
                    break
                else:
                    flag = 'H'

            if flag == 'H':
                self.hit(hand, shoe)

            if flag == 'P':
                self.split(hand, shoe)

            if flag == 'S':
                break

    def hit(self, hand, shoe):
        c = shoe.deal()
        hand.add_card(c)
        if db: print "Hitted: %s" % c

    def split(self, hand, shoe):
        self.hands.append(hand.split())
        if db: print "Splitted %s" % hand
        self.play_hand(hand, shoe)


class Dealer(object):
    """
    Represent the dealer
    """
    def __init__(self, hand=None):
        self.hand = hand

    def set_hand(self, new_hand):
        self.hand = new_hand

    def play(self, shoe):
        while self.hand.value < 17:
            self.hit(shoe)

    def hit(self, shoe):
        c = shoe.deal()
        self.hand.add_card(c)
        if db: print "Dealer hitted: %s" %c

class Game(object):
    """
    A sequence of Blackjack Rounds that keeps track of total money won or lost
    """
    def __init__(self):
        self.shoe = Shoe(SHOE_SIZE)
        self.money = 10000 # start with 10k
        self.bet = 0.0
        self.stake = 1.0
        self.player = Player()
        self.dealer = Dealer()

    def get_hand_winnings(self, hand):
        win = 0.0
	bet = self.stake
        if not hand.surrender:
            if hand.busted():
                status = "LOST"
            else:
                if hand.blackjack():
                    if self.dealer.hand.blackjack():
                        status = "PUSH"
                    else:
                        status = "WON 3:2"
                elif self.dealer.hand.busted():
                    status = "WON"
                elif self.dealer.hand.value < hand.value:
                    status = "WON"
                elif self.dealer.hand.value > hand.value:
                    status = "LOST"
                elif self.dealer.hand.value == hand.value:
                    if self.dealer.hand.blackjack():
                        status = "LOST"  # player's 21 vs dealers blackjack
                    else:
                        status = "PUSH"
        else:
            status = "SURRENDER"

	if stutzer_mode: # bet 5% of money on each hand 
 	    # in an attempt to make stutzer's strat more consistently losing,
	    # this game removes surrendering and 3:2 odds
	    if strict_rules:
	        bet *= (self.get_money()*0.05) # bet 5% of your money
	        if status == "LOST":
                    win += -bet
                elif status == "WON":
                    win += bet
                elif status == "WON 3:2":
                    win += bet
                elif status == "SURRENDER":
                    win += -bet
    	        else: 
    	            if db: 
    	        	    print "STATUS == 0"
                    if hand.doubled:
                        win *= 2
                        bet *= 2
	    else:
	        bet *= (self.get_money()*0.05) # bet 5% of your money
	        if status == "LOST":
                    win += -bet
                elif status == "WON":
                    win += bet
                elif status == "WON 3:2":
                    win += 1.5 * bet
                elif status == "SURRENDER":
                    win += -0.5 * bet
    	        else: 
    	            if db: 
    	        	    print "STATUS == 0"
                    if hand.doubled:
                        win *= 2
                        bet *= 2
	    #bet *= self.stake
	else: # original mode not relevant to this paper
            if status == "LOST":
                win += -1
            elif status == "WON":
                win += 1
            elif status == "WON 3:2":
                win += 1.5
            elif status == "SURRENDER":
                win += -0.5
            if hand.doubled:
                win *= 2
                bet *= 2
	    win *= self.stake

	if db: print(status + " Hand: " + str(hand))
	
	if db: print("WIN: " + str(win) + " BET: " + str(bet))
        return win, bet

    def play_round(self):
        # this is the ONLY place where we bet based on count
	if card_counting:
	    if self.shoe.truecount() > 6:
                self.stake = BET_SPREAD
	    else:
	    	self.stake = 1.0
        else:
            self.stake = 1.0

        player_hand = Hand([self.shoe.deal(), self.shoe.deal()])	
        dealer_hand = Hand([self.shoe.deal()])
        self.player.set_hands(player_hand, dealer_hand)
        self.dealer.set_hand(dealer_hand)

	# for parrondo's paradox, we will play two hands simultaneously
	if parrondo_mode:
	    second_player_hand = Hand([self.shoe.deal(), self.shoe.deal()])
	    self.player.hands.append(second_player_hand)

        if db: print "Dealer Hand: %s" % self.dealer.hand
        if db: print "Player Hand: %s\n" % self.player.hands[0]

        self.player.play(self.shoe)
        self.dealer.play(self.shoe)

        if db: print ""
	if db: print("Money before: " + str(self.money))

	winnings = 0 # add winnings to self.money after ALL hands played
		     # since bet for a hand is dependent on self.money
        bettings = 0 
#      	print("Player hands:")
#	for i in range(len(self.player.hands)):
#	    print(self.player.hands[i])
#	print("Dealer Hand:") 
#	print(dealer_hand)

	for hand in self.player.hands:
            win, bet = self.get_hand_winnings(hand)
            winnings += win
	    bettings += bet
            if db: print "Player Hand: %s (Value: %s, Busted: %d, BlackJack: %r, Splithand: %r, Soft: %r, Surrender: %r, Doubled: %r)" % (hand, hand.value, hand.busted(), hand.blackjack(), hand.splithand, hand.soft(), hand.surrender, hand.doubled)

        self.money += winnings
	self.bet += bettings

	if db: print "Dealer Hand: %s (%d)" % (self.dealer.hand, self.dealer.hand.value)
	if db: print "Bet: " + str(bettings) + " Money after: " + str(self.get_money())

    def get_money(self):
        return self.money

    def get_bet(self):
        return self.bet


def run_game():
	moneys = []
        bets = []
        countings = []
        nb_hands = 0
        for g in range(GAMES):
            game = Game()
            while not game.shoe.reshuffle:
                # print '%s GAME no. %d %s' % (20 * '#', i + 1, 20 * '#')
                game.play_round()
                nb_hands += 1

            moneys.append(game.get_money())
            bets.append(game.get_bet())
            countings += game.shoe.count_history

            if see_results: print("WIN for Game no. %d: %s (%s bet)" % (g + 1, "{0:.2f}".format(game.get_money()), "{0:.2f}".format(game.get_bet())))

        sume = 0.0
        total_bet = 0.0
        for value in moneys:
            sume += value
        for value in bets:
            total_bet += value

        init_money = 0
        if stutzer_mode:
            init_money = 10000*GAMES # money you started with

        print "\n%d hands overall, %0.2f hands per game on average" % (nb_hands, float(nb_hands) / GAMES)
        print "%0.2f total bet" % total_bet
        # print("Init money" + str(init_money))
        print("Overall winnings: {} (edge = {} %)".format("{0:.2f}".format(sume), "{0:.3f}".format(100.0*(sume-init_money)/total_bet)))

        # graph of winnings
        #moneys = sorted(moneys)
        #fit = stats.norm.pdf(moneys, np.mean(moneys), np.std(moneys))
        #pl.plot(moneys, fit, '-o')
        #pl.hist(moneys, normed=True)
        #pl.show()

        # a graph of the frequency of each card count
        #plt.ylabel('count')
        #plt.plot(countings, label='x')
        #plt.legend()
        #plt.show()

	return (100.0*(sume-init_money)/total_bet)


# =======DEMO SECTION=======
if __name__ == "__main__":
    importer = StrategyImporter(sys.argv[1])
    HARD_STRATEGY, SOFT_STRATEGY, PAIR_STRATEGY = importer.import_player_strategy()
        
    db = False
    see_results = False
    strict_rules = True
    card_counting = True
    GAMES = 100000



	#LOOKING FOR THE BUG THAT SETS BETS TO BE NEGATIVE SOMETIMES!!!! HOW!!!
    # #PREDEMO SANDBOX
    # print("=======PREDEMO=======")
    # stutzer_mode = True
    # parrondo_mode = True
    # see_results = True
    # db = True
    # run_game()











    
    # BEGIN DEMO
    
    # BASIC GAME
    print("Beginning demonstration of Parrondo's paradox")
    print("If you find that the demo is taking too long, you can set GAMES lower, but be aware the results will be much less accurate. We recommend GAMES > 100000")
    print("Each section takes a little under 5 minutes if GAMES == 100000")
    print("")

    print("=======BASIC GAME=======") 
    print("First, a game of Blackjack:")
    print("Player bets $1 every round. Bets more if count is high.") 

    parrondo_mode = False
    stutzer_mode = False
   
    print("")
    print("Running...")
    if (run_game() > 0):	
	print("")
    	print("Notice this is a positive outcome")
	print("The player uses basic strategy and card counting to achieve a positive outcome")
    else:
    	print("")
    	print("OOPS, it failed; this should have been a positive outcome. This has never happened before; something's wrong.")

    
    # STUTZER GAME
    print("=======STUTZER'S GAME=======")
    print("Next, we demo Michael Stutzer's game:")
    print("Player starts with $10000 and bets 5% of their money each round")

    stutzer_mode = True

    print("")
    print("Running...")
    if (run_game() < 0):
    	print("")
	print("Notice this is a negative outcome")
	print("The player uses the same basic strategy and card counting as in the basic game but still has a negative outcome due to their betting strategy")
    else:
	print("")
    	print("OOPS, it failed; this should have been a negative outcome. This very rarely fails, so just try again.")


    # PARRONDO GAME
    print("=======PARRONDO GAME=======")
    print("Finally, we demonstrate Parrondo's parradox")
    print("Here, we play Stutzer's game, but the player plays 2 hands at once")

    parrondo_mode = True

    print("")
    print("Running...")
    if (run_game() > 0):
	print("")
    	print("Notice this is a positive outcome")
	print("Paradoxically, playing two games at once using the same losing strategy in each yields a positive result")
	print("This is Parrondo's paradox")
    else:
	print("")
    	print("OOPS, it failed; this should have been a positive outcome. This fails a little more often than the other games, so try a few more times. It averages out to a positive outcome.")

