from hand_strength import *
from atom_funcs import * 
import numpy as np

playing_deck = {rank + suit for rank in ranks for suit in suits}

""" --- Helper functions --- """
def turn_prob(outs, cards_left = 45):
    """
    Probability of drawing one of the outs on the turn
    Assumes 45 cards left: 52 - 3 - 2 - 2 
    (3 flop, 2 in player 1, 2 in player 2's hand)

    Args:
        outs: (set) of cards/outs

    Returns:
        float: probability

    """
    num_outs = len(outs)

    return num_outs/cards_left

def add_to_river(outs, flush_outs, straight_outs):
    first_miss = playing_deck.difference((flush_outs | straight_outs) | outs)
    add_to_river = (len(first_miss)/45)*(len(outs)/44)
    return add_to_river

def river_prob(outs, cards_left = 45):
    """
    Probability of drawing one of the outs by the river
    (strictly greater than turn_prob)

    Assumes 45 cards left: 52 - 3 - 2 - 2 
    (3 flop, 2 in player 1, 2 in player 2's hand)

    Args:
        outs: (set) of cards/outs

    Returns:
        float: probability

    """
    
    num_outs = len(outs)

    connect_on_turn = num_outs/cards_left
    connect_on_river = (1 - connect_on_turn) * (num_outs/(cards_left - 1)) 
    
    river_prob = connect_on_turn + connect_on_river
    return river_prob

def card_str_to_card_set(cards_str):
    """
    Get set of cards from string representation of cards

    Args:
        card_str: e.g. 5h9h

    Returns:
        set(str): e.g. {'5h', '9h'}
    
    """
    ranks, suits = get_cards(cards_str)
    return set([x + y for x, y in zip(ranks, suits)])

def get_valid_outs(seen_cards, valid_ranks, valid_suits = suits):
    """
    From ranks/numbers, get all cards (excluding cards in seen_cards)
    
    Args:
        seen_cards: set() of cards that can't be included in outs
        valid_ranks: List[str] of ranks e.g. [A, 7]

    Returns:
        set(str) of cards (outs)
    """

    res = set()
    for r in valid_ranks:
        for s in valid_suits:
            curr_card = r + s
            if curr_card not in seen_cards:
                res.add(curr_card)

    return res

def num_cards_of_this_rank(seen_cards, valid_ranks, valid_suits = suits):
    """
    Given list of numbers/ranks and seen cards, return the # of outs

    Args:
        seen_cards (set) of cards
        valid_ranks: List[str]

        valid_suits: parameter to specify if we only want a certain suit

    Returns:
        int: # of outs
    
    
    """


    res = 0
    for r in valid_ranks:
        for s in valid_suits:
            curr_card = r + s
            if curr_card not in seen_cards:
                res += 1

    return res

# NEED TO ACCOUNT FOR WHEN STATIC_RANKS is ppairs!!!
def pp_extra_river_prob(board_ranks, static_ranks):
    """ Account for extraneous pocket pairs that may appear on turn/river,
        leading to (1 pair -> 2 pair ) or (3kind -> full house)
    """
    assert len(static_ranks) == 2, "can only have 2 cards in hand"
    
    static1, static2 = static_ranks[0], static_ranks[1]
    
    board_ranks = set(board_ranks)
    num_ppairs = 13 - len(board_ranks)

    if static1 != static2:
        # 1st term: nums not in static_hand. 2nd term: nums in static_hand
        if (static1 not in board_ranks) and (static2 not in board_ranks):
            res = (((num_ppairs - 2)*4*3)+(2*3*2))/(45*44)
            res =  (num_ppairs*4*3)/(45*44)
        else:
            res = (((num_ppairs - 1)*4*3)+(1*3*2))/(45*44)
    else:
        if (static1 not in board_ranks):
            res = (((num_ppairs - 1)*4*3)+(1*2*1))/(45*44)
        else:
            res = (num_ppairs*4*3)/(45*44)

    return res

def pp_extra_river_prob_alt(board_ranks, static_ranks, is_flush_draw, flush_draw_outs, straight_draw_outs):
    """ Alternative implementation of ^
    """
    assert len(static_ranks) == 2, "can only have 2 cards in hand"
    
    board_ranks_set = set(board_ranks)

    unique_straight_draw_ranks = {card[0] for card in straight_draw_outs}

    non_board_ranks_set = set(ranks).difference(board_ranks_set)
    non_board_ranks_set = non_board_ranks_set.difference(unique_straight_draw_ranks)

    static_ranks_set = set(static_ranks)

    flush_draw_ranks = {c[0] for c in flush_draw_outs}


    if len(static_ranks_set) == 2:
        # these 2 are mutually exclusive (mathematically)
        ranks_with_4_left = non_board_ranks_set.difference(static_ranks_set)
        ranks_with_3_left = non_board_ranks_set.intersection(static_ranks_set)



        if is_flush_draw:
            three_left = ranks_with_4_left.intersection(flush_draw_ranks)
            four_left = ranks_with_4_left.difference(flush_draw_ranks)

            two_left = ranks_with_3_left.intersection(flush_draw_ranks)
            also_three_left = ranks_with_3_left.difference(flush_draw_ranks)

            a = len(four_left)
            b = len(three_left) + len(also_three_left)
            c = len(two_left)

            res = ( (a*4*3) + (b*3*2) + (c*2*1) )/(45*44)

            return res

        else:    
            a = len(ranks_with_4_left)
            b = len(ranks_with_3_left)

            res = ( (a*4*3) + (b*3*2) )/(45*44)

    elif len(static_ranks_set) == 1:

        ranks_with_4_left = non_board_ranks_set.difference(static_ranks_set)
        ranks_with_2_left = non_board_ranks_set.intersection(static_ranks_set)

        if is_flush_draw:
            three_left = ranks_with_4_left.intersection(flush_draw_ranks)
            four_left = ranks_with_4_left.difference(flush_draw_ranks)

            # one left...not enough
            two_left = ranks_with_2_left.difference(flush_draw_ranks)

            a = len(four_left)
            b = len(three_left)
            c = len(two_left)

            res = ( (a*4*3) + (b*3*2) + (c*2*1) )/(45*44)

        else:
            a = len(ranks_with_4_left)
            b = len(ranks_with_2_left)

            res = ( (a*4*3) + (b*2*1) )/(45*44)

    return res
  

""" --- One pair stuff ---"""
def one_pair_outs(opp_nums, flop_nums, seen_cards, min_pair_rank = 0):
    """
    Return outs that would lead to 1 pair to be made.
    Excludes already made pairs.

    When called in one_pair_prob, only considers ranks in hand
    (not ranks in flop...by designs since I only want to consider
    pairs where the hand is involved)

    Args:
        opp_nums(List[int]): The numbers in opp's hand
        flop_nums(List[int]): The numbers on flop
        seen_cards: Set of cards (to remove from possible outs)
    
        min_pair_rank: If we only care about numbers higher than some rank

    Returns:
        set(str) of outs that would lead to 1 pair made: e.g. {'Ad', 'Th', 'Ts', 'Td', 'As'}
    """


    # Ranks that would lead to a higher pair if connected (excludes already made pairs)
    valid_ranks = [card_dict[n] for n in opp_nums if (n > min_pair_rank) and (n not in flop_nums)]
    res = get_valid_outs(seen_cards, valid_ranks)

    return res


def one_pair_prob(hand_type, one_card_outs, flush_draw_outs = set(), straight_draw_outs = set()):
    """
    Probability of making a pair on the turn and river
    If a pair or better is already made, return 100% prob

    Args:
        hand_type (int): the hand type
        one_pair_outs (set): set of outs

    Returns:
        float: probability of hitting on turn
        float: probability of hitting by the river
    """

    turn, river = 0, 0 

    # edge cases
    if hand_type >= 1:
        return 1, 1

    turn = turn_prob(one_card_outs)

    added_river = add_to_river(one_card_outs, flush_draw_outs, straight_draw_outs)
    river = turn + added_river

    return turn, river

""" --- Two pair stuff ---"""

def second_pair_outs(opp_ranks, flop_ranks, pair_rank, seen_cards, min_pair_rank = 0):
    """(Only called when opp_hand_type = 1 pair)
    
    Returns outs that would improve hand from 1 pair to 2 pair

    Args:
        opp_ranks (List[str])
        flop_ranks (List[str])
        pair_rank(int): What pair has already been made
    
    
    """
    
    # deal with pocket pairs
    if opp_ranks[0] == opp_ranks[1]:
        valid_ranks = flop_ranks

    # flop ranks: 5 5 8 (must include at least 1 rank from hand)
    elif len(set(flop_ranks)) == 2:
        valid_ranks = opp_ranks

    else:
        # determine which rank is not paired yet
        missing_rank = opp_ranks[0]
        if opp_ranks[0] == pair_rank:
            missing_rank = opp_ranks[1]

        valid_ranks = [r for r in flop_ranks if r != pair_rank]
        valid_ranks.append(missing_rank)

    res = get_valid_outs(seen_cards, valid_ranks)
    
    return res


def two_pair_gut_shot_prep(opp_ranks, flop_ranks, seen_cards):
    rank1, rank2 = opp_ranks[0], opp_ranks[1]
    flop1, flop2, flop3 = flop_ranks[0], flop_ranks[1], flop_ranks[2]

    rank1_qty = num_cards_of_this_rank(seen_cards, [rank1])
    rank2_qty = num_cards_of_this_rank(seen_cards, [rank2])

    flop1_qty = num_cards_of_this_rank(seen_cards, [flop1])
    flop2_qty = num_cards_of_this_rank(seen_cards, [flop2])
    flop3_qty = num_cards_of_this_rank(seen_cards, [flop3])

    return rank1_qty, rank2_qty, flop1_qty, flop2_qty, flop3_qty

def prob_two_pair_gut_shot(r1, r2, f1, f2, f3):
    """
    For a gut shot to land, you need to connect at least 1 card from your hand 
    (and then any of the other cards in your hand or the flop)


    Effectively:
    2 (ab + ac + ad + ae 
          + bc + bd + be) where a,b are hand and c,d,e is flop cards

    Returns:
        float: probability of hitting a gut shot (0 pair -> 2 pair on turn and river)
    
    """


    term1 = 2*r1*(r2 + f1 + f2 + f3)
    term2= 2*r2*(r1 + f1 + f2 + f3)
    term3 = 2*r1*r2

    res = (term1 + term2 - term3)/(45*44)
    return res


def two_pair_probs(opp_hand_type, opp_ranks, flop_ranks, static_ranks, 
                   pair_rank, seen_cards, is_flush_draw = False, min_pair_rank = 0, 
                   flush_draw_outs = set(), straight_draw_outs = set()):
    """
    Returns probability of 2 pair
    
    Args:
        opp_hand_type(int): hand type at flop
        opp_ranks (List[str]): hand
        flop_ranks (List[str]) flop
        static_ranks (List[str]) other person's hand
        pair rank (str): rank of paired hand e.g. 'K'
        seen_cards (str): cards alread out 

    """
    turn, river = 0, 0 

    # edge cases
    if opp_hand_type >= 2:
        return 1, 1

    # one pair made already
    if opp_hand_type == 1:

        # excludes cards that would lead to flush
        one_card_outs = second_pair_outs(opp_ranks, flop_ranks, pair_rank, seen_cards)
        # exclude one-card outs that would lead to flush
        if is_flush_draw:
            one_card_outs = one_card_outs.difference(flush_draw_outs)


        one_card_outs = one_card_outs.difference(straight_draw_outs)


        turn = turn_prob(one_card_outs)
        
        added_river = add_to_river(one_card_outs, flush_draw_outs, straight_draw_outs)
        river = turn + added_river

        # All 2 in a row pairs not included in flop + opp hand
        """ PROBLEM IS HERE """
        other_ppairs = pp_extra_river_prob_alt(opp_ranks + flop_ranks, static_ranks, is_flush_draw, flush_draw_outs, straight_draw_outs)
        river += other_ppairs

    elif opp_hand_type == 0:
        r1, r2, f1, f2, f3 = two_pair_gut_shot_prep(opp_ranks, flop_ranks, seen_cards)
        river = prob_two_pair_gut_shot(r1, r2, f1, f2, f3)

    return turn, river

# Frozen set probs

def frozenset_counts(curr_set, unwanted_ranks, qty_to_remove):
    """
    Returns remaining # of cards for each card in hand (given cards in other person's hand)
    
    Returns:
        List[int] of remaining counts of each of the 2 cards in curr_set (e.g. [4,3]) 
    """
    assert len(curr_set) == 2, "must have 2 cards in hand"
    assert ((qty_to_remove == 1) or (qty_to_remove == 2)), "can only remove 1 or 2 cards"

    counts = [0, 0]
    
    unwanted_nums = [card_toNum[i] for i in unwanted_ranks]
    if 'A' in unwanted_ranks:
        unwanted_nums.append(1)

    for i, num in enumerate(curr_set):
        if num in unwanted_nums:
            counts[i] = 4 - qty_to_remove
        else:
            counts[i] = 4

    return counts


def straight_frozenset_prob(curr_set, rank_freq_dict, turn_suit_flush = 'x', river_suit_flush = 'x', flush_draw_outs = set()):
    """
    Returns probability of hitting the 2 cards in curr_set consecutively
    EXCLUDES situations that would lead to a flush
    """

    counts = [0, 0]

    if set(rank_freq_dict) == {1}:
        counts = frozenset_counts(curr_set, rank_freq_dict[1], 1)

    elif set(rank_freq_dict) == {2}:
        counts = frozenset_counts(curr_set, rank_freq_dict[2], 2)

    # remove flush suit here!
    if turn_suit_flush != 'x':
        num1, num2 = curr_set
        
        # num to rank e.g. 'A','T', '5'
        if num1 == 1:
            rank1 = 'A'
        else:
            rank1 = card_dict[num1]
        if num2 == 1:
            rank2 = 'A'
        else:
            rank2 = card_dict[num2]
    
        special_card1 = rank1 + turn_suit_flush
        special_card2 = rank2 + turn_suit_flush

        # subtract cards that would lead to flush
        if special_card1 in flush_draw_outs:
            counts[0] = counts[0] - 1
        if special_card2 in flush_draw_outs:
            counts[1] = counts[1] - 1

    elif river_suit_flush != 'x':
        num1, num2 = curr_set
        
        if num1 == 1:
            rank1 = 'A'
        else:
            rank1 = card_dict[num1]
        if num2 == 1:
            rank2 = 'A'
        else:
            rank2 = card_dict[num2]
    
        special_card1 = rank1 + river_suit_flush
        special_card2 = rank2 + river_suit_flush

        if ((special_card1 in flush_draw_outs) and (special_card2 in flush_draw_outs)):
            
            prob = 2 * (counts[0]/45) * (counts[1]/44)

            # subtract situation that would lead to flush
            prob = prob - ((1/45)*(1/44))
            return prob
        
    counts[0] = max(counts[0], 0)
    counts[1] = max(counts[1], 0)

    prob = 2 * (counts[0]/45) * (counts[1]/44)

    return prob


def three_kind_gut_shot_prob(curr_set, rank_freq_dict, is_flush_draw = False, flush_turn_outs = set()):
    """
    Prob of going from 0 pair to 3 of a kind after turn/river

    Args:
        curr_set: set of cards in your hand
        rank_freq_dict: frequency dict of cards in other person's hand
    """

    counts = [0, 0]

    assert len(curr_set) == 2, 'must have 2 cards in hand'

    if set(rank_freq_dict) == {1}:
        counts = frozenset_counts(curr_set, rank_freq_dict[1], 1)

    # other person has pocket pairs
    elif set(rank_freq_dict) == {2}:
        counts = frozenset_counts(curr_set, rank_freq_dict[2], 2)

    # make sure we don't accidentally get a flush
    if is_flush_draw:
        n1, n2 = curr_set

        if n1 == 1:
            r1 = 'A'
        else:
            r1 = card_dict[n1]
        if n2 == 1:
            r2 = 'A'
        else:
            r2 = card_dict[n2]

        special_suit = next(iter(flush_turn_outs))[-1]
        
        card1 = r1 + special_suit
        card2 = r2 + special_suit

        if card1 in flush_turn_outs:
            counts[0] -= 1
        if card2 in flush_turn_outs:
            counts[1] -= 1

    # not necessary but just in case
    counts[0] = max(0, counts[0])
    counts[1] = max(0, counts[1])

    card1_prob = (counts[0]/45)*((counts[0] - 1)/44)
    card2_prob = (counts[1]/45)*((counts[1] - 1)/44)

    return card1_prob + card2_prob


""" --- Three kind stuff ---"""
def three_kind_outs_turn(seen_cards, pair_rank):
    """
    Get the remaining outs for the rank of the pair I already made

    E.g. If I have K pair...look for remaining K outs
    """
    res = get_valid_outs(seen_cards, pair_rank)
    return res

def two_in_a_row_prob(rank, static_ranks):
    """
    Given rank and cards in other person's hand, what is probability
    of drawing that rank 2 times in a row? (assumes 45 cards left after flop)

    Explanation:

    Suppose there is an 8 on the flop. What's the prob that becomes 3oak?
        - if no 8s in other person's hand...then 3 x 2/(45x44)
        - if 1 8 in other person'a hand...then 2x1/(45x44)
        - if other person has pocket 8s...then no chance

    Args:
        rank (str)
        static_ranks(List[str])

    Returns:
        float
    """

    if rank in static_ranks:
        if static_ranks[0] == static_ranks[1]:
            to_add = 0
        else:
            to_add = 2 * 1
    else:
        to_add = 3 * 2

    prob = to_add/(45*44)
    return prob


def three_kind_probs(hand_type, pair_rank, hand_ranks, static_ranks, seen_cards,
                     is_flush_draw = False, flush_turn_outs = set(), straight_draw_outs = set()):

    """    
    Args:
        hand_type(int): hand type made on flop
        pair_rank (str): If they made a pair, what is the rank of their pair? e.g. T 
        hand_ranks(List[str]): The ranks in player's hand
        static_ranks (List[str]): ranks in other person's hand
        seen_cards: Set of cards (to remove from possible outs)

    """
    turn, river = 0, 0

    # if you have 2 pair...you can't make 3oak...only full house
    if hand_type == 2:
        return 0, 0

    if hand_type >= 3:
            return 1, 1

    if hand_type == 1:
        #pair_rank = card_dict[opp_hand_ranks[0]] #can substitute with pair rank
        one_card_outs = three_kind_outs_turn(seen_cards, pair_rank)

        turn = turn_prob(one_card_outs)
        added_river = add_to_river(one_card_outs, flush_turn_outs, straight_draw_outs)
        river = turn + added_river
    
    elif hand_type == 0:
        static_hand_rank_freq = board_freq(static_ranks)
        hand_nums_set = set([card_toNum[r] for r in hand_ranks])

        river = three_kind_gut_shot_prob(hand_nums_set, static_hand_rank_freq, 
                                         is_flush_draw, flush_turn_outs)
    
    return turn, river


""" --- Straight stuff ---"""

# Straight: Finding draw nums (yet to turn to rank)
def find_straight_draw_from_3cards(desc_sorted_arr):
    
    """
    Returns set of frozenset of draws (size 2) needed to go from 3 cards to a straight
    E.g. 3,4,5 would need (1,2) or (2,6) or (6,7)

    Possible diffs: {1,1}, {1,2}, {1,3}, {2,2}. If any other scenario, can't get to straight
    with just 2 cards

    Returns:
        set{frozenset{(a,b)}} of draws

    """
    # NEED MAKE SURE len(desc_sorted_arr) == 3
    assert len(desc_sorted_arr) == 3, "Find straight draw from 3 cards: need input of 3 cards"
    # e.g. (1,2) means need both a 1 and a 2 to make a straight
    consecutive_draws = set()

    min, max = desc_sorted_arr[-1], desc_sorted_arr[0]

    one, two, three  = 0, 0, 0
    in_between = 0

    for i in range(1, len(desc_sorted_arr)):
        curr_diff = desc_sorted_arr[i-1] - desc_sorted_arr[i]
        if curr_diff == 2:
            two += 1
            in_between = desc_sorted_arr[i] + 1
        elif curr_diff == 1:
            one += 1
        elif curr_diff == 3:
            three += 1
            in_between = desc_sorted_arr[i] + 1
    
    # 3, 4, 5
    if one == 2:
        if max + 2 <= 14:
            consecutive_draws.add(frozenset({max + 1, max + 2}))
        if min - 2 >= 1:
            consecutive_draws.add(frozenset({min - 1, min - 2}))
        if max + 1 <= 14 and min - 1 >= 1:
            consecutive_draws.add(frozenset({min - 1, max + 1}))

    # 3, 4, 6
    elif (one == 1) and (two == 1):
        if max + 1 <= 14:
            consecutive_draws.add(frozenset({in_between, max + 1}))
        if min - 1 >= 1:
            consecutive_draws.add(frozenset({in_between, min - 1}))

    # 3, 4, 7
    elif (one == 1) and (three == 1):
        consecutive_draws.add(frozenset({in_between, in_between + 1}))

    # 3 5 7
    elif two == 2:
        consecutive_draws.add(frozenset({min + 1, max - 1}))

    return consecutive_draws

def find_straight_draw_from_4cards(desc_sorted_arr):
    """Assumes arr is sorted in desc order"""
    assert all(
    desc_sorted_arr[i] >= desc_sorted_arr[i + 1]
    for i in range(len(desc_sorted_arr) - 1)
    ), "Array is not sorted in descending order"


    # edge case
    straight_draws = set()
    missing_num = -1

    # count times diff by 1, 2
    one_count, two_count = 0, 0
    for i in range(1, len(desc_sorted_arr)):
        curr_diff = desc_sorted_arr[i-1] - desc_sorted_arr[i]
        if curr_diff == 2:
            two_count += 1
            missing_num = desc_sorted_arr[i] + 1
        elif curr_diff == 1:
            one_count += 1
        # if diff by more than 2...no chance
        else:
            return straight_draws

    # consecutive (only diff by 1)  
    if two_count == 0:
        draw1, draw2 = desc_sorted_arr[0] + 1, desc_sorted_arr[-1] - 1
        if (draw1 <= 14) and (draw1 >= 1):
            straight_draws.add(draw1)
        if (draw2 <= 14) and (draw2 >= 1):
            straight_draws.add(draw2)

    # only missing 1
    elif two_count == 1:
        straight_draws.add(missing_num)

    return straight_draws

def straight_draws_turn(arr):
    """
    Returns: Set(int) draws
    """ 

    # Make sure to sort array in descending order (and remove duplicates)
    arr = list(set(arr))
    arr.sort(reverse = True)
    

    res = set()
    # min length: 4
    if len(arr) < 4:
        return res
    
    for i in range(3, len(arr)):
        curr_arr = arr[i-3: i+1]
        res.update(find_straight_draw_from_4cards(curr_arr))

    return res

def straight_draws_river(arr, opp_nums):
    """
    Finds all scenarios where having 2 more cards would lead to a straight

    How: Slide window of size 3 across array, looking for set of 2 cards that would
    lead to straight


    Returns: Set(frozenset(x,y)) draws
    """

    arr = list(set(arr))
    arr.sort(reverse = True)

    res = set()

    # min length: 3
    if len(arr) < 3:
        return res
    
    for i in range(2, len(arr)):
        curr_arr = arr[i-2: i+1]

        # hand needs to be involved
        if all(num not in curr_arr for num in opp_nums):
            continue

        res.update(find_straight_draw_from_3cards(curr_arr))

    return res

def filter_pairs(unfiltered_sets: set, unwanted_ranks):
    """
    From set of frozenset{(a,b)}, remove pairs where either a,b is in unwanted_nums

    Args:
        unfiltered_set: set{  frozenset({a,b}) } of unfiltered pairs
        unwanted_nums: List[str] of 
        
    Res:
        set{  frozenset({a,b}) } of pairs after filtering
    
    """

    filtered_sets = set()
    while unfiltered_sets:
        curr_set = unfiltered_sets.pop()
        rank1, rank2 = curr_set

        if (rank1 not in unwanted_ranks) and (rank2 not in unwanted_ranks):
            filtered_sets.add(curr_set)

    return filtered_sets 

# Convert from draw nums to draw cards

def straight_one_outs(opp_nums, flop_nums, seen_cards, min_rank = 0, turn_suit_flush = 'x'):
    """
    Finds the single cards to complete a straight draw

    Returns:
        res: set() of cards
        outs_ranks: List[str] of ranks
    """ 

    straight_draw_nums = opp_nums + flop_nums
    if 14 in straight_draw_nums:
        straight_draw_nums.append(1)

    outs_nums = straight_draws_turn(straight_draw_nums)

    # deal with 1 <--> A edge case
    outs_ranks = [card_dict[n] for n in outs_nums if (n > min_rank) and (n != 1)]

    # edge case: 1
    if 1 in outs_nums:
        outs_ranks.append('A')

    # filter suits that would turn into flush
    non_flush_suits = list( set(['h', 'd', 's', 'c']) - set([turn_suit_flush]) )
    res = get_valid_outs(seen_cards, outs_ranks, valid_suits=non_flush_suits)

    return res, outs_ranks

def straight_gutshot_prob(opp_nums_orig, flop_nums, static_ranks, restricted_ranks = [], turn_suit_flush = 'x', river_suit_flush = 'x', flush_draw_outs = set()):
    """
    Returns probability of making a straight gut shot 
    (need 2 cards to make a straight...then hit both on turn/river)
    """

    opp_nums = opp_nums_orig.copy()

    total_prob = 0

    if 14 in opp_nums:
        opp_nums.append(1)

    nums = opp_nums + flop_nums

    unwanted_nums = set(nums)
    unwanted_nums.update(set(restricted_ranks))

    # All 2-card pairs that would lead to a straight if both drawn
    draw_pair_sets = straight_draws_river(nums, opp_nums)
    draw_pair_sets = filter_pairs(draw_pair_sets, unwanted_nums)

    static_hand_rank_freq = board_freq(static_ranks)

    while draw_pair_sets:
        curr_set = draw_pair_sets.pop()
        curr_prob = straight_frozenset_prob(curr_set, static_hand_rank_freq, 
                                            turn_suit_flush = turn_suit_flush, 
                                            river_suit_flush = river_suit_flush,
                                            flush_draw_outs = flush_draw_outs)
        total_prob += curr_prob

    return total_prob

def straight_probs(opp_hand_type, opp_nums_orig, flop_nums, static_ranks, seen_cards, 
                  suit_counts_dict, straight_draw_outs, flush_draw_outs = set()):
    """
    
    Args:
        opp_nums: List[int] of opp's ranks in int format
        opp_nums: List[int] of flop ranks in int format
    
    """
    opp_nums = opp_nums_orig.copy()

    turn_suit_flush = 'x'
    river_suit_flush = 'x'

    if 4 in suit_counts_dict:
        turn_suit_flush = suit_counts_dict[4][0]

    if 3 in suit_counts_dict:
        river_suit_flush = suit_counts_dict[3][0]

    if opp_hand_type >= 4:
        return 1, 1

    straight_turn_prob, straight_river_prob = 0, 0

    # determine if we can make a straight with just 1 more card
    one_card_outs, one_card_ranks = straight_one_outs(opp_nums, flop_nums, seen_cards, min_rank = 0, 
                                                      turn_suit_flush = turn_suit_flush)
    
    straight_draw_outs.update(one_card_outs)

    # if only 1 out is needed
    if one_card_outs:
        straight_turn_prob = turn_prob(one_card_outs)
        straight_added_river = add_to_river(straight_draw_outs, flush_draw_outs, set())
        straight_river_prob = straight_turn_prob + straight_added_river

        one_card_nums = [card_toNum[r] for r in one_card_ranks]
        
        # excludes 1 card draws
        extra_gutshot = straight_gutshot_prob(opp_nums, flop_nums, static_ranks,
                                              restricted_ranks=one_card_nums, 
                                              turn_suit_flush = turn_suit_flush, river_suit_flush = river_suit_flush,
                                              flush_draw_outs = flush_draw_outs)
        straight_river_prob += extra_gutshot
    
    # if 2 outs are needed
    else:
        straight_river_prob = straight_gutshot_prob(opp_nums, flop_nums, static_ranks, 
                                                    restricted_ranks=[], 
                                                    turn_suit_flush = turn_suit_flush, river_suit_flush = river_suit_flush,
                                                    flush_draw_outs = flush_draw_outs)

    return straight_turn_prob, straight_river_prob

""" --- Flush stuff --- """
def flush_draw_details(suit_counts_dict):
    """
    Find the drawing suit. There can only be 1, because you need
    at least 3 cards for a chance to make a flush, and there cannot
    be more than 1 suit with 3 cards given 5 cards (3 in flop, 2 in hand)

    Output: suit, qty_draws_needed
    """
    if 5 in suit_counts_dict.keys():
        return (suit_counts_dict[5], 0)
    if 4 in suit_counts_dict.keys():
        return (suit_counts_dict[4], 1)
    if 3 in suit_counts_dict.keys():
        return (suit_counts_dict[3], 2)
    
    # no chance (or already made flush)
    return ('x', -1)

def get_flush_outs(hand: str, flop: str, seen_cards):
    # get suit + draws_needed
    suit_counts_dict = suit_counts(flop + hand) # {2: ['d'], 1: ['c']}
    valid_suit, qty_draws_needed = flush_draw_details(suit_counts_dict)

    if valid_suit == 'x':
        return (set(), -1) 

    # board_nums: numbers of that suit that are already revealed
    board_ranks = get_ranks(hand + flop, valid_suit[0])
    board_nums = [card_toNum[r] for r in board_ranks]

    valid_nums = [i for i in range(2, 15) if i not in board_nums]
    valid_ranks = [card_dict[n] for n in valid_nums]

    res = get_valid_outs(seen_cards, valid_ranks, valid_suits = valid_suit)
    return res, qty_draws_needed

def flush_prob_turn(flush_outs, cards_needed):
    if cards_needed == 1:
        return turn_prob(flush_outs)
    
    return 0

def flush_prob_river(flush_outs, cards_needed):
    if cards_needed == 1:
        return river_prob(flush_outs)
    
    elif cards_needed == 2:
        num_outs = len(flush_outs)
        return (num_outs/45)*((num_outs - 1)/44)

    return 0


def flush_probs(opp_hand_type, hand: str, flop: str, seen_cards: str, flush_draw_outs: set):
    """
    
    Args:
        opp_hand_tpe(int)
        hand (str): e.g. '7c9h'
        flop (str): e.g. '2d8c7d'
        seen_cards: set of seen cards

    """
    # returns empty set if no flush outs
    flush_outs, cards_needed = get_flush_outs(hand, flop, seen_cards)
    flush_draw_outs.update(flush_outs)

    if opp_hand_type >= 5:
        return 1, 1

    turn = flush_prob_turn(flush_outs, cards_needed)
    river = flush_prob_river(flush_outs, cards_needed)

    return turn, river


def one_pair_to_full_house(pair_rank, other_rank, static_ranks):
    """
    Assuming we have 1 pair, what's the prob of getting to full house by river?
    
    pair_rank: The rank of the paired card
    other_rank: The rank of the non-paired card
    
    """
    assert len(static_ranks) == 2, "can only have 2 cards in hand"

    pair_rank_outs = 2
    other_rank_outs = 3

    if static_ranks[0] == static_ranks[1]:
        if static_ranks[0] == pair_rank:
            pair_rank_outs -= 2
        if static_ranks[0] == other_rank:
            other_rank_outs -= 2
    else:
        for r in static_ranks:
            if r == pair_rank:
                pair_rank_outs -= 1
            if r == other_rank:
                other_rank_outs -= 1

    pair_rank_outs = max(0, pair_rank_outs)
    other_rank_outs = max(0, other_rank_outs)

    prob = 2 * (pair_rank_outs * other_rank_outs)/(45*44)
    return prob


def full_house_probs(opp_hand_type, flop_plus_hand_nums, flop_ranks, static_ranks, seen_cards):
    """
    Probabilities of full house on turn/river

    Args:
        opp_hand_type(int)
        flop_plus_hand_nums(List[int])
        flop_ranks: List[str]
        static_ranks: List[str]
        seen_cards: set(str) of seen cards (e.g {'Ad', '4s'})
    
    """

    turn, river = 0, 0
    
    opp_hand_ranks = [card_dict[n] for n in flop_plus_hand_nums]

    if opp_hand_type >= 6:
        return 1, 1

    # if 2 pair
    if opp_hand_type == 2:
        pair1_rank, pair2_rank = opp_hand_ranks[0], opp_hand_ranks[2]
        last_rank = opp_hand_ranks[-1]

        one_card_outs_ranks = [pair1_rank, pair2_rank]
        one_card_outs = get_valid_outs(seen_cards, one_card_outs_ranks)
        
        turn = turn_prob(one_card_outs)
        river = river_prob(one_card_outs)

        # Need to add last rank prob (e.g. 8 8 6 6 K) --> K
        river += two_in_a_row_prob(last_rank, static_ranks)

    elif opp_hand_type == 3:
        r2, r3 = opp_hand_ranks[3], opp_hand_ranks[4]

        one_card_outs_ranks = [r2, r3]
        one_card_outs = get_valid_outs(seen_cards, one_card_outs_ranks)

        turn = turn_prob(one_card_outs)
        river = river_prob(one_card_outs)

        # Need to add other pocket pairs
        board_ranks = flop_ranks + opp_hand_ranks

        extra_ppairs_prob = pp_extra_river_prob(board_ranks, static_ranks)
        river += extra_ppairs_prob 

    elif opp_hand_type == 1:
        pair_rank = opp_hand_ranks[0]
        other_ranks = opp_hand_ranks[2:]

        for r in other_ranks:
            # pair -> 3oak and unpaired --> pair
            river += one_pair_to_full_house(pair_rank, r, static_ranks)
            
            # ppairs
            river += two_in_a_row_prob(r, static_ranks)

    return turn, river


""" --- 4 of a kind stuff """
def four_kind_2_in_a_row(rank, static_ranks):
    if rank in static_ranks:
        to_add = 0
    else:
        to_add = 2 * 1

    prob = to_add/(45*44)
    return prob


def four_kind_probs(opp_hand_type, opp_hand_nums, opp_ranks, static_ranks, seen_cards):
    """
    Returns probabilities of 4oak on turn/river

    Args:
        opp_hand_type(int)
        opp_hand_nums (List[int])
        opp_ranks: (List[str])
        static_ranks: (List[str])
        seen_cards: set(str) of seen cards (e.g {'Ad', '4s'})
    
    """


    turn, river = 0, 0

    if opp_hand_type >= 7:
        return 1, 1
    
    elif opp_hand_type == 3:
        top_rank = card_dict[opp_hand_nums[0]]
        one_card_outs = get_valid_outs(seen_cards, [top_rank])

        turn = turn_prob(one_card_outs)
        river = river_prob(one_card_outs)

    elif opp_hand_type == 2:
        r1 = card_dict[opp_hand_nums[0]]
        r2 = card_dict[opp_hand_nums[2]]

        river += four_kind_2_in_a_row(r1, static_ranks)
        river += four_kind_2_in_a_row(r2, static_ranks)

    elif opp_hand_type == 1:
        r1 = card_dict[opp_hand_nums[0]]

        # effectively excludes flopped pair (not made pair)
        if r1 in opp_ranks:
            river += four_kind_2_in_a_row(r1, static_ranks)

    return turn, river


def straightflush_frozenset_prob(curr_set, suit_flush, flush_outs):
    """
    Adds probability if both cards are available

    e.g. If (4h, 6h) needed...and both are available...then add
    If either or both are unavailable...nothing.
    """

    # get special cards ... make sure they're both in 
    num1, num2 = curr_set
    if num1 == 1:
        rank1 = 'A'
    else:
        rank1 = card_dict[num1]
    if num2 == 1:
        rank2 = 'A'
    else:
        rank2 = card_dict[num2]

    special_card1 = rank1 + suit_flush
    special_card2 = rank2 + suit_flush

    if (special_card1 in flush_outs) and (special_card2 in flush_outs):
        prob = 2 * (1/45) * (1/44)
        return prob

    else:
        return 0 

def straightflush_gutshot_prob(opp_nums, flop_nums, suit_flush, flush_outs, restricted_ranks = []):
    total_prob = 0

    restricted_nums = [card_toNum[r] for r in restricted_ranks]
    if 14 in restricted_nums:
        restricted_nums.append(1)

    if 14 in opp_nums:
        opp_nums.append(1)
    elif 14 in flop_nums:
        flop_nums.append(1)

    nums = opp_nums + flop_nums
    unwanted_nums = set(nums)
    unwanted_nums.update(set(restricted_nums)) 

    # checks that len >= 3
    draw_pair_sets = straight_draws_river(nums, opp_nums)
    draw_pair_sets = filter_pairs(draw_pair_sets, unwanted_nums)

    # see if pair e.g. ('8h','Th') is available
    while draw_pair_sets:
        curr_set = draw_pair_sets.pop()
        curr_prob = straightflush_frozenset_prob(curr_set, suit_flush, flush_outs)

        total_prob += curr_prob

    return total_prob


def straight_flush_probs(opp_hand_type, hand: str, flop: str, seen_cards: set, suit_counts_dict, 
                         flush_draw_outs = set()):

    if opp_hand_type == 8:
        return 1, 1

    straight_flush_turn_prob = 0
    straight_flush_river_prob = 0

    suit_flush = 'x'

    if 4 in suit_counts_dict:
        suit_flush = suit_counts_dict[4][0]

    elif 3 in suit_counts_dict:
        suit_flush = suit_counts_dict[3][0]

    elif 5 in suit_counts_dict:
        suit_flush = suit_counts_dict[5][0]

    else:
        return 0, 0
    
    # we only care about 1 suit here!!
    opp_ranks_special_suit = get_ranks_by_suit(hand, suit_flush)
    flop_ranks_special_suit = get_ranks_by_suit(flop, suit_flush)
    opp_nums_special_suit = [card_toNum[r] for r in opp_ranks_special_suit]
    flop_nums_special_suit = [card_toNum[r] for r in flop_ranks_special_suit]

    existing_straightflush_nums = opp_nums_special_suit + flop_nums_special_suit
    if 14 in existing_straightflush_nums:
        existing_straightflush_nums.append(1)

    # which ranks are missing? (1 card situation)
    outs_nums = straight_draws_turn(existing_straightflush_nums)
    outs_ranks = [card_dict[n] for n in outs_nums if n != 1]
    if 1 in outs_nums:
        outs_ranks.append('A')

    # these 1 cards will lead to a straight flush
    one_card_straightflush_outs = get_valid_outs(seen_cards, outs_ranks, valid_suits = [suit_flush])

    if one_card_straightflush_outs:
        straight_flush_turn_prob = turn_prob(one_card_straightflush_outs)
        straight_flush_river_prob = river_prob(one_card_straightflush_outs)

        # exclude outs_ranks
        extra_gutshot = straightflush_gutshot_prob(opp_nums_special_suit, flop_nums_special_suit, 
                                                               suit_flush, flush_outs = flush_draw_outs,
                                                               restricted_ranks=outs_ranks)
        straight_flush_river_prob += extra_gutshot

    # Need 2 cards for straight flush
    else:
        straight_flush_river_prob = straightflush_gutshot_prob(opp_nums_special_suit, flop_nums_special_suit, 
                                                               suit_flush, flush_outs = flush_draw_outs)

    return straight_flush_turn_prob, straight_flush_river_prob

""" --- Overall function --- """

def opp_stats(flop_str, hand_str, opp_hand_str):
   
    """
    Returns the probabilities that opponent achieves each hand type on flop/turn/river
    given inputted flop and hero's hands

    Args:
        flop_str (str): The 3 cards on flop. E.g. 'Kc7cTs'
        hand_str: The 2 cards in your hand: E.g. 'Kd3c'
        opp_hand_str: The 2 cards in opponent's hand: E.g. ''7d6c'

    Returns:
        final_res_table (np.array): 2d ndarray of opponent's probabilities of each hand type on flop/turn/river
        higher_pair_stats (np.array): 1d ndarray of opponent's chance of improving past hero's current hand
        is_draw_stats (np.array): 1x2 array of 0/1 representing if opp has straight/flush draw

    """
    # track hero cards
    hero_card_1 = hand_str[:2]
    hero_card_2 = hand_str[2:]
    hero_cards = [hero_card_1, hero_card_2]

    # Example: (1, [5, 5, 11, 4, 3]) custom sorted already
    opp_hand_type, flop_plus_hand_nums = hand_strength(opp_hand_str, flop_str)
    hero_hand_type, flop_plus_hero_hand_nums = hand_strength(hand_str, flop_str)

    suit_counts_dict = suit_counts(flop_str + opp_hand_str) # {2: ['d'], 1: ['c']}

    # pair_rank_num: what is the top rank of their paired/3-oak card?

    """ Do we want this when no pair made?"""
    pair_rank_num = 2 
    if opp_hand_type in {1, 2, 3}:
        pair_rank_num = flop_plus_hand_nums[0] 
    
    pair_rank = card_dict[pair_rank_num]

    # Remove these cards from outs
    seen_cards = card_str_to_card_set(hand_str + flop_str + opp_hand_str)

    # string format
    opp_ranks = get_ranks(opp_hand_str)
    flop_ranks = get_ranks(flop_str)
    static_ranks = get_ranks(hand_str)

    # int format
    opp_nums = [card_toNum[r] for r in opp_ranks]
    flop_nums = [card_toNum[r] for r in flop_ranks]

    # COMPUTE FLUSH FIRST (needed later )
    global_flush_draw_outs = set()

    # Flush (checked!)
    flush_turn, flush_river = flush_probs(opp_hand_type, opp_hand_str, flop_str, seen_cards, global_flush_draw_outs)
    is_flush_draw = int(flush_turn > 0)

    # Straight (checked!)
    global_straight_draw_outs = set()
    straight_turn, straight_river = straight_probs(opp_hand_type, opp_nums, flop_nums, 
                                                   static_ranks, seen_cards, 
                                                   suit_counts_dict, global_straight_draw_outs, flush_draw_outs = global_flush_draw_outs)


    """----------Critical pair rank--------------
    
    If hero has pair, what is probability that villain will 
    end up with a hand that's better than your current pair (if it doesn't improve)?

    higher_pair_now: Does he have a better hand now?
    
    higher_pair_turn: prob of getting a single pair that's higher rank than yours by turn
    higher_pair_river: prob of getting a single pair that's higher rank than yours by river

    Next: will have to add all the other superior turn/river probs (cap at 1)
    """
    if hero_hand_type == 1:
        hero_pair_rank = flop_plus_hero_hand_nums[0]

        # already has a better pair
        if opp_hand_type == 1:
            if pair_rank_num > hero_pair_rank:
                higher_pair_now = 1
                higher_pair_turn, higher_pair_river = 1, 1

            elif pair_rank_num == hero_pair_rank:
                higher_sorted_nums = int(flop_plus_hand_nums > flop_plus_hero_hand_nums)
                
                higher_pair_now = higher_sorted_nums
                higher_pair_turn, higher_pair_river = higher_sorted_nums, higher_sorted_nums
            
            else:
                higher_pair_now = 0
                higher_pair_turn, higher_pair_river = 0, 0

                # later: add superior turns, rivers (cap at 1 tho)
            
        elif opp_hand_type > 1:
            higher_pair_now, higher_pair_turn, higher_pair_river = 1, 1, 1
            
        elif opp_hand_type == 0:
            higher_pair_now = 0

            higher_pair_outs = one_pair_outs(opp_nums, flop_nums, seen_cards, min_pair_rank = hero_pair_rank)
            higher_pair_outs = higher_pair_outs.difference(global_flush_draw_outs)

            higher_pair_turn = turn_prob(higher_pair_outs)
            higher_pair_added_river = add_to_river(higher_pair_outs, global_flush_draw_outs, global_straight_draw_outs)
            higher_pair_river = higher_pair_turn + higher_pair_added_river

    # last night's change here
    elif hero_hand_type == 0:
        if opp_hand_type == 0:
            higher_sorted_nums = int(flop_plus_hand_nums > flop_plus_hero_hand_nums)

            higher_pair_now = higher_sorted_nums
            higher_pair_turn, higher_pair_river = higher_sorted_nums, higher_sorted_nums

        else:
            higher_pair_now = 1
            higher_pair_turn, higher_pair_river = 1, 1

    # only valid for when hero has a pair or nothing
    else:
        higher_pair_now, higher_pair_turn, higher_pair_river = -1, -1, -1
        
    """----------Probabilities for opp to get these hands--------------"""

    # One pair (checked!)
    pair_outs = one_pair_outs(opp_nums, flop_nums, seen_cards)
    pair_outs = pair_outs.difference(global_flush_draw_outs)

    pair_turn, pair_river = one_pair_prob(opp_hand_type, pair_outs, 
                                          flush_draw_outs = global_flush_draw_outs, straight_draw_outs = global_straight_draw_outs)

    # Three kind (checked!)

    three_kind_turn, three_kind_river = three_kind_probs(opp_hand_type, 
                     pair_rank, opp_ranks, static_ranks, seen_cards,
                     is_flush_draw=is_flush_draw, flush_turn_outs=global_flush_draw_outs, straight_draw_outs = global_straight_draw_outs)
    
    
    # Two pair (checked!)
    two_pair_turn, two_pair_river = two_pair_probs(opp_hand_type, opp_ranks, 
                                                   flop_ranks, static_ranks, pair_rank, seen_cards, is_flush_draw=is_flush_draw,
                                                   min_pair_rank=0, flush_draw_outs = global_flush_draw_outs, straight_draw_outs = global_straight_draw_outs)

    is_straight_draw = int(straight_turn > 0)

    # Full house (checked!)
    fullhouse_turn, fullhouse_river = full_house_probs(opp_hand_type, flop_plus_hand_nums, 
                                                       flop_ranks, static_ranks, seen_cards)

    # Four of a kind (checked!)
    four_kind_turn, four_kind_river = four_kind_probs(opp_hand_type, flop_plus_hand_nums, opp_ranks,
                                                      static_ranks, seen_cards)
    
    # straight flush 
    straightflush_turn, straightflush_river = straight_flush_probs(opp_hand_type, opp_hand_str, flop_str, seen_cards, suit_counts_dict, 
                         flush_draw_outs = global_flush_draw_outs)
    
    # make sure not to include straight flushes in flush probs
    if opp_hand_type != 5:
        flush_turn -= straightflush_turn
        flush_river -= straightflush_river

    if opp_hand_type != 4:
        straight_turn -= straightflush_turn
        straight_river -= straightflush_river

    is_nothing = 1 if opp_hand_type == 0 else 0
    
    opp_hand_types = ['nothing', 'pair', 'two pair', '3oak', 'straight', 'flush', 'full house', '4oak', 'straight flush']
    
    curr_probs = [0] * len(opp_hand_types)
    curr_probs[opp_hand_type] = 1
    
    turn_probs = [is_nothing, pair_turn, two_pair_turn, three_kind_turn, straight_turn, flush_turn, fullhouse_turn, four_kind_turn, straightflush_turn]
    river_probs = [is_nothing, pair_river, two_pair_river, three_kind_river, straight_river, flush_river, fullhouse_river, four_kind_river, straightflush_river]

    # adjust probabilities (e.g. if i have pair, I might improve, so I need to subtract from pair_turn and pair_river)
    
    """
    By this point, made sure that the probs of each hand only contains that hand specifically 
    (e.g. straight -> only straight (no straight flush). pair --> only pair (no flush)...flush -> only flush (no straight flush))

    That way, we're not double-deleting.

    Confirmed that probs at indices >= opp_hand_type = 1...
    So we need to subtract it by all hand types > opp_hand_type
    And then set all hand types < opp_hand_type = 0 --> sum(probs) = 1 
    """

    # adjust turn prob
    turn_probs[opp_hand_type] = turn_probs[opp_hand_type] - sum(turn_probs[opp_hand_type + 1:])
    if opp_hand_type > 0:
        turn_probs[:opp_hand_type] = [0] * (opp_hand_type)

    # adjust river prob
    river_probs[opp_hand_type] = river_probs[opp_hand_type] - sum(river_probs[opp_hand_type + 1:])
    if opp_hand_type > 0:
        river_probs[:opp_hand_type] = [0] * (opp_hand_type)

    # add hand types > current hand type
    if hero_hand_type == 1:
        higher_pair_turn = min(1, higher_pair_turn + sum(turn_probs[2:]) )
        higher_pair_river = min(1, higher_pair_river + sum(river_probs[2:]) )

    elif hero_hand_type == 0:
        higher_pair_turn = min(1, higher_pair_turn + sum(turn_probs[1:]) )
        higher_pair_river = min(1, higher_pair_river + sum(river_probs[1:]) )

    assert np.isclose(sum(curr_probs), 1, rtol = 1e-10), "opp_stat: row 1 doesn't add up"
    assert np.isclose(sum(turn_probs), 1, rtol = 1e-10), "opp_stat: row 2 doesn't add up"
    assert np.isclose(sum(river_probs), 1, rtol = 1e-10), "opp_stat: row 3 doesn't add up"
    
    final_res_table = np.array([curr_probs,
                                turn_probs,
                                river_probs])

    # higher_pair_stats: only used when hand_type = 1 or 0
    higher_pair_stats = np.array([higher_pair_now, higher_pair_turn, higher_pair_river])
    is_draw_stats = np.array([is_straight_draw, is_flush_draw])

    return final_res_table, higher_pair_stats, is_draw_stats



