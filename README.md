# Poker Hand vs. Range Toolkit

This Python app offers a quick, informative, and user-friendly interface for beginner poker players to analyze their hand vs. an opponent's range. In a real poker game, it is impossible to know exactly what hand your opponent has, but one can work with reasonable assumptions with the "set of possible hands they may have", known as the opponent's "range". By calculating the probabilities of each hand type in each scenario, the app can help the user gain valuable insight into the relative strength of their hand vs. their opponent, helping them answer questions such as:

- What is the probability that I currently have a stronger hand than them? 
- What is the potential for my opponent to improve their hand?
- Given the pot and the calculated probabilities, how much should I bet to get value? (induce them to call when I am ahead)
- Given my opponent's potential to improve, how much should I bet to discourage them from seeing the cards on the turn/river?
- Given the distribution of my opponent's hand strength (and their tendencies), what is the probability that they would fold to a bluff?

#### How this app was made

This app was made completely from scratch using Python's built-in libraries. The only dependency used is "pokerkit", which is an existing API one can use to generate cards, hands, and ranges. All the logic for determining hand type, assessing hand strength, calculating probabilities, and displaying the info in an interactive GUI was implemented from scratch.

## How to use

