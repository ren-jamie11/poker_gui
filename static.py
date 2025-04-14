'''
Card dictionary: maps ints to their symbol
- For instance: 2: '2'
- 10: 'T', 11:, 'J'...14:'A'
'''

ranks = ['A', 'K', 'Q', 'J', 'T', '2', '3', '4', 
         '5', '6', '7', '8', '9']
suits = ['h', 's', 'c', 'd']

playing_deck = {rank + suit for rank in ranks for suit in suits}

card_dict = {i: str(i) for i in range(2, 15)}
card_dict.update({
    14: 'A',
    10: 'T',
    11: 'J',
    12: 'Q',
    13: 'K'
})

card_toNum = {v: k for k, v in card_dict.items()}



ex_dict = {1: [2,3,4]}
ex_dict2 = {2: [4]}


# myset = {2,3}
# print(myset.pop(), myset.pop())


# myset = set()
# myset.add({3})

# curr_set = frozenset({2,3})
# rank1, rank2 = curr_set
# print(rank1, rank2)

# print(curr_set)


# test_flop_str = '8d6s7s'
# test_hand_str = '4h4s'
# test_opp_hand_str = 'Tc6d'
