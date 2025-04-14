from main_prob_functions import *

valid_ranks = {'A', 'K', 'Q', 'J', 'T', '9', '8', '7', '6', '5', '4', '3', '2'}
valid_suits = {'h', 'd', 's', 'c'}

def is_valid_hand(s, ranks = valid_ranks, suits = valid_suits):
    # must have 4 chars
    if len(s) != 4:
        return False, "Hand: Please enter 2 cards"

    r1, r2 = s[0], s[2]
    s1, s2 = s[1], s[3]

    if (r1 not in ranks) or (r2 not in ranks):
        return False, "Hand: Invalid rank"

    if (s1 not in suits) or (s2 not in suits):
        return False, "Hand: Invalid suit"
    
    c1 = s[:2]
    c2 = s[2:]

    if c1 == c2:
        return False, "Please do not enter duplicate hand cards"

    return True, "Success"

def is_valid_flop(s, ranks = valid_ranks, suits = valid_suits):
    # must have 4 chars
    if len(s) != 6:
        return False, "Flop: Please enter 3 cards"

    r1, r2, r3 = s[0], s[2], s[4]
    s1, s2, s3 = s[1], s[3], s[5]

    if (r1 not in ranks) or (r2 not in ranks) or (r3 not in ranks):
        return False, "Flop: Invalid rank"

    if (s1 not in suits) or (s2 not in suits) or (s3 not in suits):
        return False, "Flop: Invalid suit"
    
    c1 = s[:2]
    c2 = s[2:4]
    c3 = s[4:]

    if len({c1, c2, c3}) != 3:
        return False, "Please do not enter duplicate flop cards"

    return True, "Success"


# Example set up
hand_str = '4hJh'
flop_str = '3hTh5d'

# hand_valid, hand_error_msg = is_valid_hand(hand_str)
# flop_valid, flop_error_msg = is_valid_flop(flop_str)

def validity_command(hand_str, flop_str):
    msg = ''
    
    hand_valid, hand_error_msg = is_valid_hand(hand_str)
    flop_valid, flop_error_msg = is_valid_flop(flop_str)

    # check validity of separate
    if not hand_valid:
        msg = hand_error_msg
        print(msg)
    elif not flop_valid:
        msg = flop_error_msg
        print(msg)

    # check validity of combined
    board = hand_str + flop_str
    board_cards = get_cards_str(board)
    
    card_counts = Counter(board_cards)
    duplicated_cards = [card for card, v in card_counts.items() if v > 1]

    if duplicated_cards:
        msg = f'Overlapping cards: {duplicated_cards}'
        print(msg)

    else:
        msg = f"Hand: {hand_str} \nFlop: {flop_str}"
        print(msg)

    