from pokerkit import *
from static import card_dict, card_toNum, ranks, suits
from collections import Counter
from collections import defaultdict
    
#ASSESS THE STRENGTH OF HANDS
def custom_sort(arr):
    """
    Sorts numbers/card ranks first by freq, then by magnitude.

    Args:
        arr: unsorted array [11, 5, 4, 5, 3]
        
    Returns:
        sorted_arr: E.g. [5, 5, 11, 4, 3]
    """
    counts = Counter(arr)
    sorted_arr = sorted(arr, key=lambda x: (-counts[x], -x))
    
    return sorted_arr 


def board_freq(elements):
    """
    Compute the frequency of elements and group them by frequency.

    Args:
        numbers (list): E.g. [3,4,3,4,2,1]

    Returns: 
        dict: Keys = freqs, values = list of numbers with that freq
        E.g. {2: [3, 4], 1: [2, 1]}
    """

    frequency_count = Counter(elements)
    frequency_dict = defaultdict(list)

    for element, freq in frequency_count.items():
        frequency_dict[freq].append(element)
    
    frequency_dict = dict(frequency_dict)
    return frequency_dict

def board_counts(s):
    """
    Preps info needed to get hand type (pair, flush, straight etc.)

    Args:
        s (str): board. E.g.'Kd3cKc7cTs'

    Returns:
        1. nums sorted by freq, magnitude
        2. List[char] of suits
        3. Dict of num freqs. E.g. {2: [13], 1: [3, 7, 10]}
        4. Dict of suits freq E.g. {1: ['d', 's'], 3: ['c']}
    """

    nums = [card_toNum[s[i]] for i in range(0, len(s), 2)]
    suits = [s[i + 1] for i in range(0, len(s), 2)]

    return custom_sort(nums), suits, board_freq(nums), board_freq(suits)


def rank_counts(s):
    """
    Args:
        s (str): board. E.g.'Kd3cKc7cTs'

    Returns: 
        Dict of num freqs. E.g. {2: [13], 1: [3, 7, 10]}
    """
    

    nums = [card_toNum[s[i]] for i in range(0, len(s), 2)]
    return board_freq(nums)

def suit_counts(s):
    """
    Args:
        s (str): board. E.g.'Kd3cKc7cTs'

    Returns:
        Dict of suits freq E.g. {1: ['d', 's'], 3: ['c']}
    """

    suits = [s[i + 1] for i in range(0, len(s), 2)]
    return board_freq(suits)


def board_rank_sort(s):
    """
    Args:
        s (str): board. E.g.'Kd3cKc7cTs'

    Returns:
        nums sorted by freq, magnitude e.g. [13, 13, 10, 7, 3]
    """

    nums = [card_toNum[s[i]] for i in range(0, len(s), 2)]
    return custom_sort(nums)

# get ranks that have a specific suit
def get_ranks_by_suit(card_str, suit):
    ranks = []
    for i in range(0, len(card_str), 2):
        rank = card_str[i]
        card_suit = card_str[i + 1]
        if card_suit == suit:
            ranks.append(rank)
    return ranks


# Check Hand Types

def check_flush(suits_count):
    """
    Check if flush is present (5 of same suit).
    Assumes 5 cards

    Args:
        suits_count(dict): E.g. 1: ['d', 's'], 3: ['c']}

    Returns:
        bool: True is there is a suit with freq 5
    """

    return 5 in suits_count.keys()

# Assumes sorted!!!
def check_straight(numbers): 
    """
    Check if straight is present (5 consecutive numbers)
    Assumes 5 cards, sorted in descending order

    Args:
        numbers: E.g. [13, 13, 10, 7, 3]

    Returns:
        bool: True is there is 5 conseutive
    """


    if (numbers == [14, 5, 4, 3, 2]):
        return True

    for i in range(1, 5):
        if (numbers[i] != numbers[i-1] - 1):
            return False

    return True

def check_straight_flush(suits_count, numbers):
    return check_flush(suits_count) and check_straight(numbers)

def check_full_house(nums_count):
    return (2 in nums_count.keys()) and (3 in nums_count.keys())

def check_four_kind(nums_count):
    return 4 in nums_count.keys()

def check_three_kind(nums_count):
    return (3 in nums_count.keys()) and (1 in nums_count.keys())

def check_two_pair(nums_count):
    if 2 not in nums_count.keys():
        return False
    
    if len(nums_count[2]) == 2:
        return True
    
    return False

def check_pair(nums_count):
    if 2 not in nums_count.keys():
        return False
    
    if len(nums_count[2]) == 1:
        return True
    
    return False

def hand_strength(hand, flop):
    
    '''
    Given flop + hand, determine best hand

    Args:
        hand(str): 'Kd3c'
        flop(str): 'Kc7cTs'
        

    Returns:
        hand_type(int): number representing pair, 2 pair...full house etc.
        nums: custom-sorted ranks

        E.g. (1, [13, 13, 10, 7, 3])
    '''

    board = hand + flop
    nums, suits, nums_count, suits_count = board_counts(board)

    hand_type = 0

    is_Flush = check_flush(suits_count)
    is_Straight = check_straight(nums)

    if is_Straight:
        if is_Flush:
            hand_type = 8
        else:
            hand_type = 4
        return (hand_type, nums)

    elif is_Flush: 
        hand_type = 5
        return (hand_type, nums)

    if check_four_kind(nums_count):
        hand_type = 7
        return (hand_type, nums)

    elif check_full_house(nums_count):
        hand_type = 6
        return (hand_type, nums)

    elif check_three_kind(nums_count):
        hand_type = 3
        return (hand_type, nums)

    elif check_two_pair(nums_count):
        hand_type = 2
        return (hand_type, nums)

    elif check_pair(nums_count):
        hand_type = 1
        return (hand_type, nums)
    
    # nothing
    return (0, nums)

hand_type_dict= {
    0: 'none',
    1: 'one pair',
    2: 'two pair',
    3: '3oak',
    4: 'straight',
    5: 'flush',
    6: 'full house',
    7: '4oak',
    8: 'straight flush'
}


def trying():
    hand = 'Kd3c'
    flop = 'Kc7cTs'

    board = hand + flop
    print(board)
    nums, suits, nums_count, suits_count = board_counts(board)
    print("Ranks", nums)
    print("Suits", suits)
    print("Nums count", nums_count)
    print("Suits count", suits_count)

    print("Hand strength:")
    print(hand_strength(hand, flop))
