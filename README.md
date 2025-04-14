# Poker Hand vs. Range Toolkit

This Python app offers a quick, informative, and user-friendly interface for beginner poker players to analyze their hand vs. an opponent's range. In a real poker game, it is impossible to know exactly what hand your opponent has, but one can work with reasonable assumptions with the "set of possible hands they may have", known as the opponent's "range". By calculating the probabilities of each hand type in each scenario, the app can help the user gain valuable insight into the relative strength of their hand vs. their opponent, helping them answer questions such as:

- What is the probability that I currently have a stronger hand than them? 
- What is the potential for my opponent to improve their hand?
- Given the pot and the calculated probabilities, how much should I bet to get value? (induce them to call when I am ahead)
- Given my opponent's potential to improve, how much should I bet to discourage them from seeing the cards on the turn/river?
- Given the distribution of my opponent's hand strength (and their tendencies), what is the probability that they would fold to a bluff?

#### How this app was made

This app was made completely from scratch using Python's built-in libraries. The only dependency used is "pokerkit", which is an existing API one can use to generate cards, hands, and ranges. All the logic for determining hand type, assessing hand strength, calculating probabilities, and displaying the info in an interactive GUI was implemented from scratch. </br>

## How to use

We will assume a 52-card deck with ```ranks = ['A', 'K', 'Q', 'J', 'T', '2', '3', '4', '5', '6', '7', '8', '9']``` and ```suits = ['h', 's', 'c', 'd']```.

1. Enter your hand and the flop cards in string format (e.g. you have 'AdTc', the flop comes 'Ac8d3s')
2. Press "configure hand" (to check input validity and load into program)
3. Use the grid buttons to configure opponent's hand range (use side buttons to select suited/offsuit hands)
4. Press "calculate odds"

## Interpreting results

### Hero and villain stats

Hero stats shows the probabilities of each hand type for you (hero) on turn/flop/river. Likewise for villain stats. The probabilities of each column must sum to 1.

### Villain equity

Provides an upper and lower bound for the opponent's probability of beating you (hero) on turn/flush/river. 

**Upper bound**: Calculated as the probability that the opponent will acquire a hand that is better than hero's current hand. Villain equity cannot be higher than that, because it is effectively assumes hero's chance of not improving is 100%. To include more scenarios would mean to include those where villain's hand type is worse than hero's current hand

**Lower bound:** Lower bound is calculated by multiplying the upper bound ^ by (1 - P[hero hand improves]). We know villain's equity is at least this value, because villain wins if hero remains same and villain improves past hero. This number is effectively assuming hero will win so long as he/she improves.

In general, the upper/lower bound will be wider if hero has a lot of potential to improve their hand.






