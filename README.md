PARRONDO'S PARADOX
=============================================

A fork of seblau's BlackJack-Simulator as a demonstration of Parrondo's Paradox.

Parrondo's Paradox describes a situation in which two losing strategies combine to form a winning strategy.
It was conceived in the field of game theory but has applications in fields from evolutionary biology to economics. 

In this case, the demonstration starts with a demo of a basic game of Blackjack where the player bets $1 each time. With card counting and basic Blackjack strategy, the player wins a large sum of money. 

The second part shows a game imagined by Michael J. Stutzer from UC Boulder, described in his paper "A Simple Parrondo Paradox." In the game, the player starts with $10,000 and bets 5% of their money every round. Even with card counting, which gives the player a theoretic edge, the player surprisingly loses money in the long run. The simulation demonstrates what Micahel Stutzer proved to be true in theory in his paper. 

Finally, the game demonstrates Parrondo's paradox: the player plays exactly the same way, but plays two hands at the same time. Stutzer theorizes that the additional possibility, that instead of simply losing or winning 5% the player can break even (losing one hand and winning the other), causes a positive outcome. And indeed the simulation demonstrates this. 



Here's an example of the output:

> ✗ python BlackJack.py strategy/BasicStrategy.csv
> Beginning demonstration of Parrondo's paradox
> If you find that the demo is taking too long, you can set GAMES lower, but be aware the results will be much less accurate. We recommend GAMES > 100000
> Each section takes a little under 5 minutes if GAMES == 100000
> 
> =======BASIC GAME=======
> First, a game of Blackjack:
> Player bets $1 every round. Bets more if count is high.
> 
> Running...
> 
> 4228732 hands overall, 42.29 hands per game on average
> 10597915.00 total bet
> Overall winnings: 1000102033.50 (edge = 9436.781 %)
> 
> Notice this is a positive outcome
> The player uses basic strategy and card counting to achieve a positive outcome
> =======STUTZER'S GAME=======
> Next, we demo Michael Stutzer's game:
> Player starts with $10000 and bets 5% of their money each round
> 
> Running...
> 
> 4228851 hands overall, 42.29 hands per game on average
> 3692650329.34 total bet
> Overall winnings: 769210164.85 (edge = -6.250 %)
> 
> Notice this is a negative outcome
> The player uses the same basic strategy and card counting as in the basic game but still has a negative outcome due to their betting strategy
> =======PARRONDO GAME=======
> Finally, we demonstrate Parrondo's parradox
> Here, we play Stutzer's game, but the player plays 2 hands at once
> 
> Running...
> 
> 2865205 hands overall, 28.65 hands per game on average
> 17396475639.19 total bet
> Overall winnings: 3735564888.88 (edge = 15.725 %)
> 
> Notice this is a positive outcome
> Paradoxically, playing two games at once using the same losing strategy in each yields a positive result
> This is Parrondo's paradox











See original README by seblau below for details on the specifics of the Blackjack simulation and card counting.
==============================================


BlackJack-Simulator with OMEGA II Card Counting
==============================================

Flexible BlackJack-Simulator written in Python. It takes a given basic strategy as input (defined in a .csv-file) and simulates that strategy over a given amount of time. The simulator also counts cards sticking to the [OMEGA II Count](http://www.countingedge.com/card-counting/advanced-omega-ii/), which basically gives every card some value. Depending on the current count the bet size gets adjusted.

### Running

    python BlackJack.py strategy/BasicStrategy.csv

Omega II Count:

| 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | J | Q | K | A |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| +1 | +1 | +2 | +2 | +2 | +1 | 0 | -1 | -2 | -2 | -2 | -2 | 0 |

So, for example if there is a player-favorable count like +20 by 2 decks remaining, the simulator bets the standard bet times the specified *BET_SPREAD*.

### Definition of Terms

The simulator involves several concepts related to Blackjack game play:
* A *Hand* is a single hand of Blackjack, consisting of two or more cards
* A *Round* is single round of Blackjack, in which one or more players play their hands against the dealer's hand
* A *Shoe* consists of multiple card decks consisting of SHOE_SIZE times 52 cards
* A *Game* is a sequence of Rounds that starts with a fresh *Shoe* and ends when the *Shoe* gets reshuffled

### Result

The simulator provides the net winnings result per game played and an overall result summing up all the game results. The following output for example  indicates, that in game no. 67 the simulated player won 18 hands more than he lost. On the other hand in game no. 68 the simulator lost 120 hands more than he won.

     ...
     WIN for Game no. 67: 18.000000
     WIN for Game no. 68: -120.000000
     ...

This graph displays every game with its total won or lost hands. You can see that in some rare games about 60 more hands are lost/won than won/lost. If the expectation is positive, you have developed a *Winning BlackJack Strategy*, which is the case for the provided BasicStrategy plus the OMEGA II count.

![Gaussian Distribution](/documentation/gaussian.png?raw=true)

This graph displays the development of the count for each game. You can see that the card count in rare cases even exceeds 40 and is on average as you would expect 0.

![Counts Distribution](/documentation/counts.png?raw=true)

### Gaming Rules

The simulator plays with the following casino rules:

* Dealer stands on soft 17
* Double down after splitting hands is allowed
* No BlackJack after splitting hands
* 3 times 7 is counted as a BlackJack

### Configuration Variables

| Variable        | Description         |
| ------------- |-------------|
| *GAMES*  | The number of games that should be played |
| *ROUNDS_PER_GAME*  | The number of rounds that should be played per game (may cover multiple shoes) |
| *SHOE_SIZE*   | The number of decks that are used |
| *SHOE_PENETRATION*  | Indicates the percentage of cards that still remain in the shoe, when the shoe gets reshuffled |
| *BET_SPREAD*  | The multiplier for the bet size in a player favorable counting situation |

### Sample Configuration

    GAMES = 1
    ROUNDS = 10
    SHOE_SIZE = 8
    SHOE_PENETRATION = 0.2 # reshuffle after 80% of all cards are played
    BET_SPREAD = 20.0 # Bet 20-times the money if the count is player-favorable
    
### Strategy

Any strategy can be fed into the simulator as a .csv file. The default strategy that comes with this simulator looks like the following:

![Default Strategy](/documentation/strategy.png?raw=true)

* The first column shows both player's cards added up
* The first row shows the dealers up-card
* S ... Stand
* H ... Hit
* Sr ... Surrender
* D ... Double Down
* P ... Split

### Note on the shuffle method used
The shuffle method used is the default random.shuffle() which comes with a warning :  
*"[if] the total number of permutations of x is larger than the period of most random number generators, [then] most permutations of a long sequence can never be generated."*  
https://docs.python.org/2/library/random.html  
Hopefully :  
"Python uses the Mersenne Twister as the core generator. It produces 53-bit precision floats and has a period of 2**19937-1"
Which means that a list of over ~~2080 elements would never see all its permutations, even if it got shuffled an infinite number of times. 8x52 = 416 is low enough to ignore this problem.

