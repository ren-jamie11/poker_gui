import tkinter as tk
from validity_check import *
from tkinter import ttk
import time

root = tk.Tk()
root.title("Poker Starting Hand Grid (Jamie)")
root.geometry("1480x800")

""" --- Frame/grid set up--- """
left_frame = tk.Frame(root)
left_frame.grid(row=0, column=0, padx=10, pady=20)

right_frame = tk.Frame(root)
right_frame.grid(row=0, column=1, sticky='nw', padx=50)

""" --- Left frame --- """

ranks = ['A', 'K', 'Q', 'J', 'T', '9', '8', '7', '6', '5', '4', '3', '2']
suits = ['h', 'd', 's', 'c']

global buttons
buttons = []  # 2D list to store button references

# Add label at the top
left_title = tk.Label(left_frame, text="Hand range", font=("Helvetica", 16, "bold"))
left_title.grid(row=0, column=0, columnspan=13, pady=10)

range_count_label = tk.Label(left_frame, text="Cards in range", font=("Helvetica", 12))
range_count_label.grid(row=16, column=0, columnspan=13, pady=10, sticky = 'w')

# Explanation box frame
explanation_frame = tk.Frame(left_frame, bd=1, relief='solid', padx=5, pady=5)
explanation_frame.grid(row=17, column=0, columnspan=13, rowspan=2, pady=10, sticky='w')

# First line: bolded
explain_title_label = tk.Label(
    explanation_frame,
    text="Villain equity bounds",
    font=("Helvetica", 8, "bold"),
    anchor='w',
    justify='left'
)
explain_title_label.pack(anchor='w')


# Rest of the explanation
explain_text_label = tk.Label(
    explanation_frame,
    text=(
        "Upper bound: P [villain surpasses hand you currently have]  \t \n"
        "Lower bound: P [villain surpasses hand you currently have] * P [you do not improve your hand] \t"
    ),
    font=("Helvetica", 8),
    anchor='w',
    justify='left'
)
explain_text_label.pack(anchor='w')

# range object
global opp_range
opp_range = set()

global on_offs
on_offs = [[False for i in range(13)] for j in range(13)]

global hand_table
hand_table = []    

def card_command(i: int, j:int):
    global hand_table
    global opp_range
    global on_offs
    global buttons

    cards = parse_range(hand_table[i][j])

    if not on_offs[i][j]:
        opp_range.update(cards)
        on_offs[i][j] = True
        
        buttons[i][j].config(bg = 'white', underline = 1, border = 2)
        range_count_label.config(text = f"Cards in range: {len(opp_range)}")

    else:
        opp_range = opp_range.difference(cards)
        on_offs[i][j] = False

        if i == j:
            buttons[i][j].config(bg = '#D3DECD', underline = -1, border = 2)
        elif i < j:
            buttons[i][j].config(bg = '#F1E5C9', underline = -1, border = 2)
        else:
            buttons[i][j].config(bg = '#DDE2F7', underline = -1, border = 2)

        range_count_label.config(text = f"Cards in range: {len(opp_range)}")

# Start grid from row=1 instead of 0
for i, row_rank in enumerate(ranks):
    row_buttons = []
    row_hand_strs = []

    for j, col_rank in enumerate(ranks):
        if i == j:
            hand = f"{row_rank}{col_rank}"       # Pair
            button_color = '#D3DECD'
        elif i < j:
            hand = f"{row_rank}{col_rank}s"      # Suited
            button_color = '#F1E5C9'
        else:
            hand = f"{col_rank}{row_rank}o"      # Offsuit
            button_color = '#DDE2F7'
            
        btn = tk.Button(left_frame, text=hand, bg=button_color, width=5, height=2, command = lambda i = i, j = j: card_command(i, j))
        #btn = tk.Button(root, text=hand, bg=button_color, width=5, height=2)
        btn.grid(row=i + 1, column=j, padx=1, pady=1)  # Shift row down by 1

        row_hand_strs.append(hand)
        row_buttons.append(btn)
    
    hand_table.append(row_hand_strs)
    buttons.append(row_buttons)

""" --- Multiple button control --- """
# Column control
col_on_offs = [False] * 13  # Tracks if each column is ON or OFF
def col_control_command(j):  # j = column index
    global opp_range
    global col_on_offs
    global on_offs
    global hand_table

    if not col_on_offs[j]:
        # Turn ON all buttons in this column
        col_on_offs[j] = True

        for i in range(13):  # each row

            if i > j:
                on_offs[i][j] = True
                opp_range.update(parse_range(hand_table[i][j]))

                # color 
                buttons[i][j].config(bg = 'white', underline = 1, border = 2)

        range_count_label.config(text = f"Cards in range: {len(opp_range)}")


    else:
        # Turn OFF all buttons in this column
        col_on_offs[j] = False

        for i in range(13):  # each row
            
            if i > j:

                on_offs[i][j] = False
                opp_range.difference_update(parse_range(hand_table[i][j]))
                
                # color
                buttons[i][j].config(bg = '#DDE2F7', underline = -1, border = 2)

        range_count_label.config(text = f"Cards in range: {len(opp_range)}")


# Buttons to press each row
value_to_rank = {14: 'A', 13: 'K', 12: 'Q', 11: 'J', 10: 'T'}

for col in range(12):
    val = 14 - col
    label = value_to_rank.get(val, str(val))  # Convert 14→'A', 13→'K', ..., else keep number

    select_col_button = tk.Button(
        left_frame,
        text=label + 'o',
        width=5,
        command=lambda j = col: col_control_command(j)
    )
    select_col_button.grid(row=15, column=col, padx=1, pady=5)

# Row control
row_on_offs = [False] * 13  # Tracks if each row is ON or OFF
def row_control_command(i):  # i = row index
    global opp_range
    global row_on_offs
    global on_offs
    global hand_table

    if not row_on_offs[i]:
        # Turn ON all buttons in this row
        row_on_offs[i] = True

        for j in range(13):  # each column
        
            # OFF SUIT 
            if i < j:

                on_offs[i][j] = True
                opp_range.update(parse_range(hand_table[i][j]))

                # Color
                buttons[i][j].config(bg='white', underline=1, border=2)

        range_count_label.config(text=f"Cards in range: {len(opp_range)}")


    else:
        # Turn OFF all buttons in this row
        row_on_offs[i] = False

        for j in range(13):  # each column

            if i < j:

                on_offs[i][j] = False
                opp_range.difference_update(parse_range(hand_table[i][j]))

                # Restore original color
                buttons[i][j].config(bg='#F1E5C9', underline=-1, border=2)
            
        range_count_label.config(text=f"Cards in range: {len(opp_range)}")


for row in range(12):
    val = 14 - row
    label = value_to_rank.get(val, str(val))  # Convert 14→'A', 13→'K', ..., else keep number

    select_row_button = tk.Button(
        left_frame,
        text=label + 's',
        width=5,
        command=lambda i=row: row_control_command(i)
    )
    select_row_button.grid(row=row + 1, column=13, padx=5, pady=1)


# Diagonal
diag_on = False  # Tracks whether the diagonal is selected

def diag_control_command():
    global diag_on
    global opp_range
    global on_offs
    global hand_table

    if not diag_on:
        diag_on = True
        for i in range(13):
            on_offs[i][i] = True
            opp_range.update(parse_range(hand_table[i][i]))
            buttons[i][i].config(bg='white', underline=1, border=2)

        range_count_label.config(text=f"Cards in range: {len(opp_range)}")


    else:
        diag_on = False
        for i in range(13):
            on_offs[i][i] = False
            opp_range.difference_update(parse_range(hand_table[i][i]))
            buttons[i][i].config(bg='#D3DECD', underline=-1, border=2)

        range_count_label.config(text=f"Cards in range: {len(opp_range)}")


diag_button = tk.Button(
    left_frame,
    text="ppairs",
    width=5,
    command=diag_control_command
)
diag_button.grid(row=15, column=13, padx=5, pady=1)



grid_on = False  # Tracks if entire grid is ON or OFF
def grid_control_command():
    global grid_on
    global opp_range
    global on_offs
    global hand_table

    global row_on_offs
    global col_on_offs
    global diag_on

    if not grid_on:

        grid_on = True
        row_on_offs = [True] * 13
        col_on_offs = [True] * 13
        diag_on = True

        for i in range(13):
            for j in range(13):
                on_offs[i][j] = True
                opp_range.update(parse_range(hand_table[i][j]))
                buttons[i][j].config(bg='white', underline=1, border=2)

        range_count_label.config(text=f"Cards in range: {len(opp_range)}")


    else:
        grid_on = False
        grid_on = False
        row_on_offs = [False] * 13
        col_on_offs = [False] * 13
        diag_on = False

        for i in range(13):
            for j in range(13):
                on_offs[i][j] = False
                opp_range.difference_update(parse_range(hand_table[i][j]))

                # Reset to original color based on type
                if i == j:
                    bg = '#D3DECD'
                elif i < j:
                    bg = '#F1E5C9'
                else:
                    bg = '#DDE2F7'

                buttons[i][j].config(bg=bg, underline=-1, border=2)

        range_count_label.config(text=f"Cards in range: {len(opp_range)}")


grid_button = tk.Button(
    left_frame,
    text="All",
    width=5,
    command=grid_control_command
)
grid_button.grid(row=16, column=13, padx=5, pady=1)




"""--- flop and hand global variables ---"""

can_calculate = False

flop_str = ''
hand_str = ''

def validity_command():
    global flop_str
    global hand_str
    global can_calculate

    # get items from box
    msg = ''
    candidate_hand_str = e_hand.get()
    candidate_flop_str = e_flop.get()

    # make sure user entered something
    if len(candidate_hand_str) == 0:
        validity_label.config(text = "Please enter hand")
        can_calculate = False

        return

    elif len(candidate_flop_str) == 0:
        validity_label.config(text = "Please enter flop")
        can_calculate = False

        return
    
    # check validity of separate
    hand_valid, hand_error_msg = is_valid_hand(candidate_hand_str)
    flop_valid, flop_error_msg = is_valid_flop(candidate_flop_str)
    
    if not hand_valid:
        msg = hand_error_msg
        validity_label.config(text = msg)
        can_calculate = False

        return

    elif not flop_valid:
        msg = flop_error_msg
        validity_label.config(text = msg)
        can_calculate = False

        return

    # check validity of combined
    board = candidate_hand_str + candidate_flop_str
    board_cards = get_cards_str(board)
    
    card_counts = Counter(board_cards)
    duplicated_cards = [card for card, v in card_counts.items() if v > 1]

    if duplicated_cards:
        msg = f'Overlapping cards: {duplicated_cards}'
        validity_label.config(text = msg)
        can_calculate = False

        return

    # success!
    else:
        hand_str = candidate_hand_str
        flop_str = candidate_flop_str
        can_calculate = True

        msg = f"Hand: {hand_str} \t Flop: {flop_str}"
        validity_label.config(text = msg)


""" --- Right frame ---"""

# Starting column index for side panel
side_col = 14
row_offset = 5  # Align vertically with the button grid

# Add label at the top
right_title = tk.Label(right_frame, text="Stats", font=("Helvetica", 16, "bold"))
right_title.grid(row=row_offset, column=0, columnspan=13, pady=34)

# --- Hand input section ---
hand_label_text = tk.Label(right_frame, text="Hand:")
hand_label_text.grid(row=row_offset+1, column = 0, padx=(10, 0), pady=5, sticky='e')

e_hand = tk.Entry(right_frame, width=14, borderwidth=5)
e_hand.grid(row=row_offset+1, column=side_col, padx = 20, pady=5, sticky='w')

# --- Flop section ---
flop_label_text = tk.Label(right_frame, text="Flop:")
flop_label_text.grid(row=row_offset + 2, column =0, padx=(10, 0), pady=5, sticky='e')

e_flop = tk.Entry(right_frame, width=14, borderwidth=5)
e_flop.grid(row=row_offset + 2, column=side_col, padx = 20, pady=5, sticky='w')

configure_button = tk.Button(right_frame, text="Configure hand", activebackground="red", command=validity_command)
configure_button.grid(row=row_offset + +3, column=side_col, padx = 20, pady=5, sticky='w')

validity_label = tk.Label(right_frame, text="")
validity_label.grid(row=row_offset + 4, column=side_col, padx = 20, pady=5, sticky='w')

result_opp = np.array([])

""" --- Calculate probabilities --- """

def calculate_probs():
    global flop_str
    global hand_str
    global opp_range
    global can_calculate

    global result_opp

    if not can_calculate:
        calculate_label.config(text = "Please configure flop/hand")
        hand_type_label.config(text = "", font=("Helvetica", 10, "bold"))
        return
    
    elif len(opp_range) == 0:
        calculate_label.config(text = "Please add cards to range")
        hand_type_label.config(text = "", font=("Helvetica", 10, "bold"))
        return

    """ --- Calculating stats --- """
    calculate_label.config(text = "")

    start_time = time.time()
    hero_hand_type, result_opp, result_hero, opp_improve_probs, opp_draw_probs = main_function(opp_range, flop_str, hand_str)
    
    # make sure opp range is not empty
    if type(result_opp) == int:
        calculate_label.config(text = "Range is empty after filtering out hand/flop cards")
        hand_type_label.config(text = "", font=("Helvetica", 10, "bold"))
        draw_label.config(text = "")

        # Clear table
        for item in opp_tree.get_children():
            opp_tree.delete(item)  

        for item in hero_tree.get_children():
            hero_tree.delete(item)  # Clear old rows

        for item in improve_tree.get_children():
            improve_tree.delete(item)  # Clear old rows

        return
    
    hero_hand_type_str = hand_type_dict[hero_hand_type]

    elapsed_time = time.time() - start_time
    print(f"Function execution time: {elapsed_time:.4f} seconds")


    # determine if straight/flush draw
    hero_is_straight_draw = int(result_hero[1][4] > 0)
    hero_is_flush_draw = int(result_hero[1][5] > 0)

    if hero_hand_type_str == "none":
        if hero_is_straight_draw:
            if hero_is_flush_draw:
                hero_hand_type_str = 'straight & flush draw'
            else:
                hero_hand_type_str = 'straight draw'
        
        elif hero_is_flush_draw:
            hero_hand_type_str = 'flush draw'

    else:
        if hero_is_straight_draw and hero_is_flush_draw:
            if hero_hand_type_str == "straight":
                hero_hand_type_str += ' (flush draw)'
            else:
                if hero_hand_type != "flush":
                    hero_hand_type_str += ' (straight & flush draw)'
        elif hero_is_straight_draw:
            if hero_hand_type_str != "straight":
                hero_hand_type_str += ' (straight draw)'
        elif hero_is_flush_draw:
            if hero_hand_type_str != "flush":
                hero_hand_type_str += ' (flush draw)'


    # format to show on GUI
    result_opp_transpose = result_opp.transpose()
    result_hero_transpose = result_hero.transpose()

    hand_type_label.config(text = f"Hand type: {hero_hand_type_str}", font=("Helvetica", 10, "bold"))

    """ --- Update the villain table --- """
    for item in opp_tree.get_children():
        opp_tree.delete(item)  # Clear old rows

    for i, row in enumerate(result_opp_transpose):
        formatted_row = [f"{val * 100:.1f}%" for val in row]  # Convert to percentages
        opp_tree.insert("", "end", values=(row_labels[i], *formatted_row))

    """ --- Update the hero table --- """
    for item in hero_tree.get_children():
        hero_tree.delete(item)  # Clear old rows

    for i, row in enumerate(result_hero_transpose):
        formatted_row = [f"{val * 100:.1f}%" for val in row]  # Convert to percentages
        hero_tree.insert("", "end", values=(row_labels[i], *formatted_row))

    """ --- Update the improve table --- """
    for item in improve_tree.get_children():
        improve_tree.delete(item)  # Clear old rows

    hero_no_improve_probs = result_hero_transpose[hero_hand_type]
    relative_strength = hero_no_improve_probs * opp_improve_probs

    villain_strength_formatted = [f"{val * 100:.1f}%" for val in opp_improve_probs]  # Convert to percentages
    improve_tree.insert("", "end", values=(scenarios[0], *villain_strength_formatted))

    relative_strength_formatted = [f"{val * 100:.1f}%" for val in relative_strength]  # Convert to percentages
    improve_tree.insert("", "end", values=(scenarios[1], *relative_strength_formatted))

    """ --- Display their straight flush draw probs"""
    opp_straight_draw_prob, opp_flush_draw_prob = opp_draw_probs[0], opp_draw_probs[1]

    draw_label.config(text = f"Prob villain has straight draw: {opp_straight_draw_prob*100:.1f}% \nProb villain has flush draw: {opp_flush_draw_prob*100:.1f}%")

    return

calculate_button = tk.Button(right_frame, text="Calculate odds", activebackground="red", command = calculate_probs)
calculate_button.grid(row=row_offset + 5, column=side_col, padx = 20, pady=5, sticky='w')

calculate_label = tk.Label(right_frame, text="")
calculate_label.grid(row=row_offset + 6, column=side_col, padx = 20, pady=5, sticky='w')

hand_type_label = tk.Label(right_frame, text="")
hand_type_label.grid(row=row_offset + 7, column=side_col, padx = 20, pady=5, sticky='w')

blank_label = tk.Label(right_frame, text="")
blank_label.grid(row=row_offset + 8, column=side_col, padx = 20, pady=5, sticky='w')

""" --- Table --- """

# Labels
row_labels = ['none', 'pair', '2 pair', '3oak', 'straight', 'flush', 'full house', '4oak', 'straight flush']
col_labels = ['flop', 'turn', 'river']

# Create opp table widget
opp_tree = ttk.Treeview(right_frame, columns=["Type"] + col_labels, show='headings', height=9)
opp_tree.grid(row=row_offset + 12, column=side_col + 2, padx=20, pady=(10, 0), sticky='w', columnspan=2)
villain_tree_label = tk.Label(right_frame, text="Villain stats", font=("Helvetica", 10, "bold"))
villain_tree_label.grid(row=row_offset + 11, column=side_col + 2, padx = 20, pady=5, sticky='w')

opp_tree.heading("Type", text="Type")
opp_tree.column("Type", anchor='w', width=100)
for col in col_labels:
    opp_tree.heading(col, text=col)
    opp_tree.column(col, anchor='center', width=60)

# Create hero table widget
hero_tree = ttk.Treeview(right_frame, columns=["Type"] + col_labels, show='headings', height=9)
hero_tree.grid(row=row_offset + 12, column=side_col, padx=20, pady=(10, 0), sticky='w', columnspan=2)
hero_tree_label = tk.Label(right_frame, text="Hero stats", font=("Helvetica", 10, "bold"))
hero_tree_label.grid(row=row_offset + 11, column=side_col, padx = 20, pady=5, sticky='w')

hero_tree.heading("Type", text="Type")
hero_tree.column("Type", anchor='w', width=100)
for col in col_labels:
    hero_tree.heading(col, text=col)
    hero_tree.column(col, anchor='center', width=60)

# Create improve stats widget
improve_tree = ttk.Treeview(right_frame, columns=["Villain equity"] + col_labels, show='headings', height=2)
improve_tree.grid(row=row_offset + 13, column=side_col + 2, padx=20, pady=(20, 0), sticky='w', columnspan=2)

improve_tree.heading("Villain equity", text="Villain equity")
improve_tree.column("Villain equity", anchor='w', width=100)

scenarios = ['Upper bound', 'Lower bound']

for col in col_labels:
    improve_tree.heading(col, text=col)
    improve_tree.column(col, anchor='center', width=60)

# Straight/flush draw label
draw_label = tk.Label(right_frame, text="")
draw_label.grid(row=row_offset + 13, column=side_col, padx = 20, pady=5, sticky='w')

root.mainloop()

