from draw_stats_prototype import *

def frozenset_to_str(two_cards):
    """
    Turns frozenset object representing 2 cards to str format
    E.g. frozenset({Ad, As}) --> 'Ad,As'
    """

    card1, card2 = two_cards

    s1 = str(card1)[-3:-1]
    s2 = str(card2)[-3:-1]

    return s1, s2
    

def remove_cards_from_range(r, *cards):
    """
    For any set of cards (e.g. 'Ah', 'Td'), remove all hands in range r
    that contain any of those cards
    
    Args:
        cards: List[str] of cards

    Returns:
        set(frozenset({'Ac', 'Td'}), frozenset({'Ac', 'Td'})...)
    """
    cards_to_remove = set(cards)
    to_remove = set()
    
    for hand in r:
        # remove if either card1 or card2 of hand is in cards_to_remove
        x, y = frozenset_to_str(hand)
        if (x in cards_to_remove) or (y in cards_to_remove):
            to_remove.add(hand)
    
    r_filtered = r.difference(to_remove)
    return r_filtered


def filter_range(r, flop_str, hand_str):
    board = hand_str + flop_str
    cards_out = get_cards_str(board)

    r_filtered = remove_cards_from_range(r, *cards_out)

    return r_filtered


def range_vs_hand_prob_matrix(r, flop_str, hand_str, pov):
    """
    Returns:
        avg_higher_pair_opp: If hero has pair, probability of villain 
        having a better hand (flop, turn, river) 
    
    """
    # filter impossible hands out of opp's range
    r_filtered = filter_range(r, flop_str, hand_str)

    if len(r_filtered) == 0:
        return -1, -1, -1

    # calculate probabilities
    matrix = np.zeros((3,9))
    avg_higher_pair_probs = np.zeros(3)
    avg_is_draw_stats = np.zeros(2)

    for hand in r_filtered:
        s1, s2 = frozenset_to_str(hand)
        curr_opp_hand_str = s1 + s2
        
        # can switch args to get stats for other person (3rd arg is the prob)
        if pov == 'opp':
            curr_matrix, curr_higher_pair_stats, curr_is_draw_stats = opp_stats(flop_str, hand_str, curr_opp_hand_str)
        elif pov == 'hero':
            curr_matrix, curr_higher_pair_stats, curr_is_draw_stats = opp_stats(flop_str, curr_opp_hand_str, hand_str)
        
        matrix += curr_matrix
        avg_higher_pair_probs += curr_higher_pair_stats
        avg_is_draw_stats += curr_is_draw_stats

    matrix = matrix / len(r_filtered)
    avg_higher_pair_probs = avg_higher_pair_probs / len(r_filtered)
    avg_is_draw_stats = avg_is_draw_stats / len(r_filtered)

    assert np.isclose(np.sum(matrix[0]), 1, rtol = 1e-10), "Prob row 1 doesn't add up"
    assert np.isclose(np.sum(matrix[1]), 1, rtol = 1e-10), "Prob row 2 doesn't add up"
    assert np.isclose(np.sum(matrix[2]), 1, rtol = 1e-10), "Prob row 3 doesn't add up"

    return matrix, avg_higher_pair_probs, avg_is_draw_stats


def main_function(r, flop_str, hand_str):
    """
    The main function that calculates hand vs. range odds 
    (the primary function of the GUI)

    Args:
        r (set(frozenset)): The set (range) of hands that opponent might have
        flop_str (str): The cards in flop (e.g. 'QdTd5c')
        hand_str (str): Hero's cards  (e.g. 'AdQc')

    Returns:
        hero_hand_type (int): What hand hero currently has (e.g. 1 = pair...9 = straight flush)
        result_opp (np.array): 2d ndarray of opponent's probabilities of each hand type on flop/turn/river
        result_hero (np.array): 2d ndarray of hero's probabilities of each hand type on flop/turn/river
        opp_improve_probs (np.array): 1d ndarray of opponent's chance of improving past hero's current hand
        avg_is_draw_opp (np.array): 1d ndarray of opp's chance of having straight/flush draw
    """
    
    # get hero's current hand type
    hero_hand_type = hand_strength(hand_str, flop_str)[0]

    # villain's probabilities
    result_opp, avg_higher_pair_opp, avg_is_draw_opp = range_vs_hand_prob_matrix(r, flop_str, hand_str, pov = 'opp')
    
    if type(result_opp) == int:
        return -1, -1, -1, -1, -1

    # hero's probabilities
    result_hero = range_vs_hand_prob_matrix(r, flop_str, hand_str, pov = 'hero')[0]

    # sum up probs of events better than your current hand
    opp_improve_probs = np.sum(result_opp[:, hero_hand_type + 1:], axis = 1)
    if (hero_hand_type == 0) or (hero_hand_type == 1):
        opp_improve_probs = avg_higher_pair_opp

    return hero_hand_type, result_opp, result_hero, opp_improve_probs, avg_is_draw_opp




