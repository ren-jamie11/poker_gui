# https://pokerkit.readthedocs.io/en/stable/

from pokerkit import *
from static import card_dict, card_toNum, ranks, suits
from collections import Counter
from collections import defaultdict
import itertools

# card_dict: int -> str
# card_toNum: str -> int

''' Building Range: Set of hands'''

def ppairs(floor):
    return parse_range(f'{floor}{floor}+')

# Given a 
def subgrid(offsuit, suit):
    myRange = set()

    #add suited first
    for i in range(offsuit, 15):
        myRange.update(parse_range(f'{card_dict[i]}{card_dict[suit]}s+'))  #T8s+...A8s+

    #add offsuit next
    for i in range(offsuit + 1, 15):
        myRange.update(parse_range(f'{card_dict[i]}{card_dict[offsuit]}o+')) 

    return myRange

# Does NOT include pocket pairs (e.g. T --> *T except TT)
def get_all_of(rank):  
    num = card_toNum[rank]
    
    lower_cards = parse_range(f'{rank}2+')
    higher_cards = set()

    for i in range(num + 1, 15):
        higher_cards.update(parse_range(f'{card_dict[i]}{rank}'))

    all_pairs = lower_cards.union(higher_cards)
    return all_pairs


# Get all second cards (e.g. T,h means all hands that have Th)
def get_second_card(rank, suit, except_ = 'x'):  #Get all hands that contain this card (rank, suit)
    hands = set()
    all_suits = {'h', 's', 'd', 'c'}
    if except_ in all_suits:
        all_suits.remove(except_)
    
    for curr_rank in card_toNum.keys(): #2...K A
        for curr_suit in all_suits:  #h, s, d, c
            if ((curr_rank != rank) or (curr_suit != suit)):
                hands.update(parse_range(f'{rank}{suit}{curr_rank}{curr_suit}'))

    return hands

def get_all_hands():
    myRange = set()
    for rank in card_toNum.keys():
        myRange.update(parse_range(f'{rank}2+'))
    myRange.update(parse_range('22+'))
    return myRange


'''Board info: Card.parse('ThJhTd')
1. ints of the cards that appeared (allow repeats)
2. suits of the cards that appeared (allows repeats)
3. Dict of freqs of each number {2: [10], 1: [11]}
4. Dict of freqs of each suit {2: ['h'], 1: ['d']}
5. The card themselves in string form: 'ThJhTd'

'''

# store frequency of each element in dict form
# e.g. [a, a, b] --> {1: ['b'], 2: ['a']} 
def board_freq(numbers):
    frequency_count = Counter(numbers)
    frequency_dict = defaultdict(list)
    
    for element, freq in frequency_count.items():
        frequency_dict[freq].append(element)
    
    frequency_dict = dict(frequency_dict)
    return frequency_dict


def get_board_info(board_gen):
    s = ""
    for i, card in enumerate(board_gen):
        curr_rank = str(card)[-3]
        s += curr_rank
        curr_suit = str(card)[-2]
        s += curr_suit

    nums = [card_toNum[s[i]] for i in range(0, len(s), 2)]
    suits = [s[i + 1] for i in range(0, len(s), 2)]

    return nums, suits, board_freq(nums), board_freq(suits), s

# customize: get ranks only if suit = "?"

def get_cards(s):
    ranks = [s[i] for i in range(0, len(s), 2)]
    suits = [s[i + 1] for i in range(0, len(s), 2)]

    return ranks, suits

def get_cards_str(s):
    res = [s[i:i+2] for i in range(0, len(s), 2)]
    return res

def get_ranks(s, suit = 'x'):

    """
    Return ranks/numbers of cards that are of a particular suit
    (or all cards if suit = x)

    Args:
        s: string representation of cards
        e.g. Kd3cKc7cTs

    Returns:
        List[char]: e.g. ['K', 'K', 'T', '7', '3']
    """

    if suit == 'x':
        ranks = [s[i] for i in range(0, len(s), 2)]
    else:
        ranks = [s[i] for i in range(0, len(s), 2) if s[i + 1] == suit]
    return ranks

'''Made hands: simple (verified)

- ignores suits (therefore can have identical card in both board and hand)
- may have overlap (3oak includes full houses)
'''

def four_kind(num_dict, suits):
    hands = set()
    
    if len(num_dict) == 1:
        # if they're all different...no way to make 4oak
        if list(num_dict.keys())[0] == 1:
            return parse_range('')
        # if ThTsTd, then get all hands with Tc
        else:
            suit_set = {'h', 's', 'c', 'd'}
            for s in suits:
                suit_set.remove(s)
            special_suit = suit_set.pop()
            
            return get_second_card(card_dict[num_dict[3][0]], special_suit)

    # If 2 of the same      
    num_ = num_dict[2][0]
    hands = parse_range(f'{card_dict[num_]}{card_dict[num_]}')

    return hands

def full_house(num_dict):
    hands = set()
    if len(num_dict) == 1:
        if list(num_dict.keys())[0] == 1:
            return parse_range('')
        else: #3 are same
            for rank_ in card_toNum.keys():
                if card_toNum[rank_] != num_dict[3][0]:
                    hands.update(parse_range(f'{rank_}{rank_}'))  #ADD ALL CARDS

            return hands
        
    num1 = num_dict[1][0]
    num2 = num_dict[2][0]
    hands = parse_range(f'{card_dict[num1]}{card_dict[num2]}')

    return hands

def three_kind(num_dict):  #might include full house

    hands = set()

    if len(num_dict) == 1:
        # if all different e.g. 9hTc3s
        if list(num_dict.keys())[0] == 1:
            # get pocket pairs for the 3 hands (9, T, 3)
            for num in num_dict[1]:
                hands.update(parse_range(f'{card_dict[num]}{card_dict[num]}'))
            return hands  
        # if all same...return empty set
        else:
            return set()
            
    num1 = num_dict[1][0]
    num2 = num_dict[2][0]

    hands.update(parse_range(f'{card_dict[num1]}{card_dict[num1]}'))
    hands.update(get_all_of(card_dict[num2]))

    return hands

# includes full-house. #doesn't make sense for [8,8,8]
# ignores suits (can have same card in both board and your hand)
def two_pair(num_dict): 
    hands = set()
    if len(num_dict) == 1:
        if list(num_dict.keys())[0] == 1:
            for c in itertools.combinations(num_dict[1], 2):
                num1 = c[0]
                num2 = c[1]
                hands.update(parse_range(f'{card_dict[num1]}{card_dict[num2]}'))
            return hands
        else:
            return set() #doesn't make sense for [8,8,8]

    num_ = num_dict[1][0]
    hands.update(get_all_of(card_dict[num_]))

    for c in card_dict.keys(): #add other pocket pairs
        if (c != num_dict[2][0]) and (c != num_dict[1][0]):
            hands.update(parse_range(f'{card_dict[c]}{card_dict[c]}'))
    
    return hands

'''Made hands: pair-related (verified)'''

def get_all_pairs(nums):
    # connect with board
    hands = set()
    for num in nums:
        hands.update(get_all_of(card_dict[num]))

    # pocket pairs (not including with board hands)
    num_set = set(nums)
    for c in card_dict.keys():
        if c not in num_set:
            hands.update(parse_range(f'{card_dict[c]}{card_dict[c]}'))
    
    return hands

def get_top_pair(nums):
    max_num = max(nums)
    hands = set()
    hands.update(get_all_of(card_dict[max_num]))
    
    num_set = set(nums)
    
    for c in card_dict.keys(): #add pocket pairs greater than highest board card
        if (c not in num_set) and (c > max_num):
            hands.update(parse_range(f'{card_dict[c]}{card_dict[c]}'))

    return hands

def get_higher_than(num):
    hands = set()
    for n in card_dict.keys():
        if n > num:
            hands.update(get_all_of(card_dict[n]))
        
    return hands


'''Flush related'''
def get_suited_hand(suit): #eg suit = 'h' #Gets all suited hands #verified
    
    suited_hands = set()
    
    for s1 in card_toNum.keys():
        for s2 in card_toNum.keys():
            if s2 != s1:
                suited_hands.update(parse_range(f'{s1}{suit}{s2}{suit}'))
    
    return suited_hands

def get_flush_draws(nums, suits, suit_dict):  #DOES NOT CONTAIN ACTUAL FLUSH
    flush_draws = set()
    ranks = [card_dict[n] for n in nums] 
    board_type = list(suit_dict.keys())

    if board_type == [1]:
        return set()
    
    elif board_type == [3]: #CORRECT
        ranks = set(ranks)
        special_suit = suit_dict[3][0]
        
        for rank_ in card_toNum.keys():
            if rank_ not in ranks:
                flush_draws.update(get_second_card(rank_, special_suit, except_ = special_suit))  #ADD ALL CARDS

        return flush_draws

    else: #2 #CORRECT
        to_avoid = set()
        special_suit = suit_dict[2][0]
        for i in range(len(ranks)):
            if suits[i] == special_suit:
                to_avoid.add(nums[i])
        to_avoid = list(to_avoid)

        flush_draws.update(get_suited_hand(special_suit))  #first, add all suited pairs
        flush_draws.difference_update(get_second_card(card_dict[to_avoid[0]], special_suit))
        flush_draws.difference_update(get_second_card(card_dict[to_avoid[1]], special_suit))

        return flush_draws
    
def get_flush(nums, suit_dict):
    flushes = set()
    
    board_type = list(suit_dict.keys())
    if board_type == [3]:
        special_suit = suit_dict[3][0]
        flushes.update(get_suited_hand(special_suit))
        flushes.difference_update(get_second_card(card_dict[nums[0]], special_suit))
        flushes.difference_update(get_second_card(card_dict[nums[1]], special_suit))
        flushes.difference_update(get_second_card(card_dict[nums[2]], special_suit))

    return flushes
        


'''Straight related'''
def one_card_straightdraw(int_list):
    if len(int_list) != len(set(int_list)):
        return []
    
    int_list = sorted(int_list)
    possible_ints = set()
    
    # Determine the range for the starting points
    min_val = min(int_list) - 3
    max_val = max(int_list)

    # Check sequences starting from min_val to max_val
    for start in range(min_val, max_val + 1):
        consecutive_set = set(range(start, start + 5))

        for i in range(start, start + 5):
            potential_set = consecutive_set - {i}
            # Check if the original list plus one potential integer is a subset of potential_set
            if len(int_list) == 3 and set(int_list).issubset(potential_set):
                for num in consecutive_set:
                    if num not in int_list:
                        if num <= 14:
                            possible_ints.add(num)

    return sorted(possible_ints)

def get_straightdraw_2(int_list):
    if int_list[0] == int_list[1]:
        return set()
    
    int_list = sorted(int_list)
    possible_pairs = []

    # Determine the range for the starting points
    min_val = min(int_list) - 4
    max_val = max(int_list)

    # Check sequences starting from min_val to max_val
    for start in range(min_val, max_val + 1):
        consecutive_set = set(range(start, start + 5))

        for i in range(start, start + 5):
            potential_set = consecutive_set - {i}
            # Check if the original list plus the potential pair is a subset of potential_set
            if len(int_list) == 2 and set(int_list).issubset(potential_set):
                for j in range(start, start + 5):
                    if j != i and j not in int_list:
                        for k in range(start, start + 5):
                            if k != i and k != j and k not in int_list:
                                if (k <= 14) and (j <= 14):    #CARD RULES
                                    possible_pairs.append((j, k))

    return set(possible_pairs)

def find_missing_int(int_list):
    # Sort the list
    sorted_list = sorted(int_list)
    
    # Check the differences between consecutive elements
    for i in range(2):
        if sorted_list[i + 1] != sorted_list[i] + 1:
            return sorted_list[i] + 1
    
    # If no gap is found (which should not happen), return None
    return None

def find_two_missing_ints(int_list):
    # Sort the list
    sorted_list = sorted(int_list)
    
    # Calculate the expected length of a complete sequence
    min_val = sorted_list[0]
    max_val = sorted_list[-1]
    
    # Determine the range of potential consecutive integers
    full_range = list(range(min_val, max_val + 1))
    
    # Find the missing integers
    missing_ints = list(set(full_range) - set(sorted_list))
    
    # If the gap is on either side, add those potential missing integers
    if len(missing_ints) == 1:
        if min_val - 1 > 0:
            missing_ints.append(min_val - 1)
        else:
            missing_ints.append(max_val + 1)
    elif len(missing_ints) == 0:
        missing_ints.append(min_val - 1)
        missing_ints.append(max_val + 1)
    
    return sorted(missing_ints)

def get_straight_draws(nums):        
    straight_draws = set()
    #check for situations where only 1 card is needed
    one_cards = one_card_straightdraw(nums)
    for c in one_cards:
        if c == 1:
            straight_draws.update(get_all_of('A'))
            straight_draws.update(parse_range('AA'))
        else:
            straight_draws.update(get_all_of(card_dict[c]))
            straight_draws.update(parse_range(f'{card_dict[c]}{card_dict[c]}'))
            
    #situations where both cards are needed
    all_cands = set()
    for comb in itertools.combinations(nums, 2):
        if comb[0] != comb[1]:
            all_cands.update(get_straightdraw_2(comb))

    #print(all_cands)
    for pair in all_cands:
        if (pair[0] < 1 or pair[0] > 14) or (pair[1] < 1 or pair[1] > 14):
            continue
        #print(pair)
        if pair[0] == 1:
            straight_draws.update(parse_range(f'A{card_dict[pair[1]]}'))
        elif pair[1] == 1:
            straight_draws.update(parse_range(f'{card_dict[pair[0]]}A'))
        else:
            straight_draws.update(parse_range(f'{card_dict[pair[0]]}{card_dict[pair[1]]}'))

    return straight_draws

def get_straight(nums): #correct
    if len(nums) != len(set(nums)):
        return set()
    
    straights = set()
    
    example = sorted(nums)
    min_ = min(example)
    max_ = max(example)
    diffs = example[2] - example[0]

    tuple_list = set()
    
    if diffs == 2:
        tuple_list.update({(min_ - 2, min_ - 1), (min_ - 1, max_ + 1), (max_ + 1, max_ + 2)})
    
    elif diffs == 3:
        i_ = find_missing_int(example)
        tuple_list.update({(i_, min_ - 1), (i_, max_ + 1)})
    
    elif diffs == 4:
        MI = find_two_missing_ints(example)
        tuple_list.update({(MI[0], MI[1])})

    else:
        return set()
    #print(tuple_list)
    for tup in tuple_list:
        if (tup[0] <= 14 and tup[0] > 0) and (tup[1] > 0 and tup[1] <= 14):
            if tup[0] == 1:
                straights.update(parse_range(f'A{card_dict[tup[1]]}'))
            elif tup[1] == 1:
                straights.update(parse_range(f'{card_dict[tup[0]]}A'))
            else:
                straights.update(parse_range(f'{card_dict[tup[0]]}{card_dict[tup[1]]}'))

    return straights



"""
TO DO

1. Given board/hand, get strength of your hand (can use tuple ranking)
2. Rank with other hands 
    - hands that currently beat you
    - flush draws
    - straight draws

"""