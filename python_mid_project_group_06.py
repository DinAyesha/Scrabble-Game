import tkinter as tk
from tkinter import messagebox, simpledialog
import random



letters = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's']
points = [1, 45, 4, 5, 34, 23, 23, 54, 23, 2, 4, 5, 7, 8, 11, 7, 4, 5, 2]
letter_distribution = {
    'a': 9, 'b': 2, 'c': 2, 'd': 4, 'e': 12, 'f': 2, 'g': 3, 'h': 2, 'i': 9,
    'j': 1, 'k': 1, 'l': 4, 'm': 2, 'n': 6, 'o': 8, 'p': 2, 'q': 1, 'r': 6, 's': 4
}


DICTIONARY_FILE = "scrabble_dictionary.txt"
dictionary_words = set()

def load_dictionary():
    try:
        with open(DICTIONARY_FILE, 'r') as f:
            for line in f:
                dictionary_words.add(line.strip().lower())
        print(f"Loaded {len(dictionary_words)} words from dictionary")
    except FileNotFoundError:
        print(f"Dictionary file '{DICTIONARY_FILE}' not found. Word validation disabled.")

def is_valid_word(word):
    return word.lower() in dictionary_words


load_dictionary()

scores = [0, 0]  
current_player = 0  
word_history = []  
player_racks = [[], []]  
letter_bag = []  
game_over = False  

def init_letter_bag():
    bag = []
    for letter, count in letter_distribution.items():
        bag.extend([letter] * count)
    random.shuffle(bag)
    return bag

def draw_letters(player, count=7):
    global letter_bag
    if len(letter_bag) < count:
        count = len(letter_bag)
    drawn = letter_bag[:count]
    player_racks[player].extend(drawn)
    letter_bag = letter_bag[count:]
    return drawn

def validate_alpha_input(new_text):
    return new_text == "" or new_text.isalpha()

def calculate_score(word):
    tally = 0
    word = word.lower()
    for letter in word:
        if letter in letters:
            index = letters.index(letter)
            tally += points[index]
    return tally

def is_cell_empty(row, col):
    cell_text = grid_buttons[row][col]['text']
    return cell_text == "" or cell_text.startswith("R")

def check_game_over():
    global game_over
    if len(letter_bag) == 0 and len(player_racks[0]) == 0 and len(player_racks[1]) == 0:
        game_over = True
        return True

def declare_winner():
    for i in range(2):
        remaining_points = sum(points[letters.index(letter)] for letter in player_racks[i] if letter in letters)
        scores[i] -= remaining_points
    update_scores()
    
    if scores[0] > scores[1]:
        winner = "Player 1 wins!"
    elif scores[1] > scores[0]:
        winner = "Player 2 wins!"
    else:
        winner = "It's a tie!"
    
    messagebox.showinfo("Game Over", 
                       f"Final Scores:\n\nPlayer 1: {scores[0]}\nPlayer 2: {scores[1]}\n\n{winner}")
    
    place_button.config(state=tk.DISABLED)
    skip_button.config(state=tk.DISABLED)
    word_entry.config(state=tk.DISABLED)
    row_entry.config(state=tk.DISABLED)
    col_entry.config(state=tk.DISABLED)

def place_word():
    global letter_bag, game_over
    if game_over:
        return
    
    word = word_entry.get().lower()
    row = row_entry.get()
    col = col_entry.get()
    direction = direction_var.get()
    
    if not word:
        messagebox.showerror("Error", "Please enter a word")
        return
    
    if dictionary_words and not is_valid_word(word):
        messagebox.showerror("Invalid Word", f"'{word.upper()}' is not a valid word in the dictionary")
        return
    
    if not row.isdigit() or not col.isdigit():
        messagebox.showerror("Error", "Row and column must be numbers")
        return
    
    row = int(row) - 1
    col = int(col) - 1
    
    if row < 0 or row > 14 or col < 0 or col > 14:
        messagebox.showerror("Error", "Invalid grid position (1-15)")
        return
    
    if direction == "horizontal" and (col + len(word)) > 15:
        messagebox.showerror("Error", "Word doesn't fit horizontally")
        return
    elif direction == "vertical" and (row + len(word)) > 15:
        messagebox.showerror("Error", "Word doesn't fit vertically")
        return
    
    temp_rack = player_racks[current_player].copy()
    missing_letters = []
    for letter in word:
        if letter in temp_rack:
            temp_rack.remove(letter)
        else:
            missing_letters.append(letter)
    
    if missing_letters:
        messagebox.showerror("Error", f"You don't have these letters: {', '.join(missing_letters)}")
        return
    
    letters_to_place = []
    for i, letter in enumerate(word):
        if direction == "horizontal":
            target_row, target_col = row, col + i
        else:
            target_row, target_col = row + i, col
        
        cell_text = grid_buttons[target_row][target_col]['text'].lower()
        
        if direction == "horizontal" and not is_cell_empty(target_row, target_col):
            messagebox.showerror("Error", f"Cannot place word - cell at row {target_row+1}, column {target_col+1} is already occupied")
            return
        
        if direction == "vertical":
            if not is_cell_empty(target_row, target_col) and cell_text != letter:
                messagebox.showerror("Error", f"Cannot place word - existing letter '{cell_text.upper()}' at row {target_row+1}, column {target_col+1} doesn't match new letter '{letter.upper()}'")
                return
        
        if is_cell_empty(target_row, target_col) or cell_text != letter:
            letters_to_place.append((target_row, target_col, letter))
    
    score = calculate_score(word)
    scores[current_player] += score
    word_history.append((f"Player {current_player+1}", word, score))
    
    letters_used = []
    for target_row, target_col, letter in letters_to_place:
        grid_buttons[target_row][target_col].config(text=letter.upper(), bg='lightblue')
        if letter in player_racks[current_player]:
            letters_used.append(letter)
    
    for letter in letters_used:
        player_racks[current_player].remove(letter)
    
    letters_needed = 7 - len(player_racks[current_player])
    if letters_needed > 0 and letter_bag:
        draw_letters(current_player, letters_needed)
    
    update_scores()
    update_racks()
    
    if check_game_over():
        declare_winner()
        return
    
    switch_player()

def skip_turn():
    global current_player, game_over
    if game_over:
        return
    
    choice = messagebox.askyesno("Skip Turn", 
                               "Do you want to exchange letters?\n\n"
                               "Yes: Exchange some/all letters\n"
                               "No: Just pass your turn")
    
    if choice:
        current_letters = " ".join(player_racks[current_player]).upper()
        num_to_exchange = simpledialog.askinteger(
            "Exchange Letters",
            f"Your letters: {current_letters}\n\n"
            "How many letters do you want to exchange? (1-7):",
            parent=window,
            minvalue=1,
            maxvalue=7
        )
        
        if num_to_exchange is not None:
            if len(letter_bag) < num_to_exchange:
                messagebox.showinfo("Exchange Letters", 
                                  f"Only {len(letter_bag)} letters left in the bag.\n"
                                  f"You can exchange up to {len(letter_bag)} letters.")
                num_to_exchange = len(letter_bag)
            
            if num_to_exchange > 0:
                letters_to_return = player_racks[current_player][:num_to_exchange]
                letter_bag.extend(letters_to_return)
                player_racks[current_player] = player_racks[current_player][num_to_exchange:]
                draw_letters(current_player, num_to_exchange)
                messagebox.showinfo("Exchange Letters", f"Exchanged {num_to_exchange} letters.")
    
    update_racks()
    update_scores()
    word_history.append((f"Player {current_player+1}", "skipped turn", 0))
    history_text.config(state=tk.NORMAL)
    history_text.insert(tk.END, f"Player {current_player+1}: skipped turn (0)\n")
    history_text.config(state=tk.DISABLED)
    
    if check_game_over():
        declare_winner()
        return
    
    switch_player()

def switch_player():
    global current_player
    current_player = 1 - current_player
    current_player_label.config(text=f"Current Player: {current_player + 1}")
    word_entry.delete(0, tk.END)

def update_scores():
    player1_score.config(text=f"Player 1: {scores[0]}")
    player2_score.config(text=f"Player 2: {scores[1]}")
    history_text.config(state=tk.NORMAL)
    history_text.delete(1.0, tk.END)
    for player, word, score in word_history:
        history_text.insert(tk.END, f"{player}: {word} ({score})\n")
    history_text.config(state=tk.DISABLED)

def update_racks():
    player1_rack_label.config(text=f"Player 1 Letters: {' '.join(player_racks[0]).upper()}")
    player2_rack_label.config(text=f"Player 2 Letters: {' '.join(player_racks[1]).upper()}")
    letters_remaining_label.config(text=f"Letters left: {len(letter_bag)}")

def create_grid(grid_generation):
    buttons = []
    for row in range(15):
        row_buttons = []
        for col in range(15):
            text = f"R{row+1}C{col+1}"
            btn = tk.Button(
                grid_generation,
                text=text,
                width=4,
                height=1,
                relief=tk.RAISED,
                bg='#f0f0f0',
                font=('Arial', 8))
            btn.grid(row=row, column=col, padx=1, pady=1)
            row_buttons.append(btn)
        buttons.append(row_buttons)
    return buttons


window = tk.Tk()
window.title("Scrabble Game")
window.geometry("1000x750")


letter_bag = init_letter_bag()
draw_letters(0, 7)
draw_letters(1, 7)

validate_alpha = window.register(validate_alpha_input)

main_frame = tk.Frame(window)
main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

grid_frame = tk.Frame(main_frame, bg='white', bd=2, relief=tk.SUNKEN)
grid_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

grid_buttons = create_grid(grid_frame)

right_panel = tk.Frame(main_frame, width=300, bg='#f0f0f0', bd=2, relief=tk.RIDGE)
right_panel.pack(side=tk.RIGHT, fill=tk.Y, padx=(10, 0))

current_player_label = tk.Label(right_panel, text="Current Player: 1", bg='#f0f0f0', font=('Arial', 12, 'bold'))
current_player_label.pack(pady=10)

score_frame = tk.Frame(right_panel, bg='#f0f0f0')
score_frame.pack(pady=5)
player1_score = tk.Label(score_frame, text="Player 1: 0", bg='#f0f0f0')
player1_score.pack(anchor='w')
player2_score = tk.Label(score_frame, text="Player 2: 0", bg='#f0f0f0')
player2_score.pack(anchor='w')

player1_rack_label = tk.Label(right_panel, text="Letters: ", bg='#f0f0f0')
player1_rack_label.pack(pady=5, anchor='w')
player2_rack_label = tk.Label(right_panel, text="Letters: ", bg='#f0f0f0')
player2_rack_label.pack(pady=5, anchor='w')

letters_remaining_label = tk.Label(right_panel, text="Letters left: 100", bg='#f0f0f0')
letters_remaining_label.pack(pady=5)

input_frame = tk.Frame(right_panel, bg='#f0f0f0')
input_frame.pack(pady=10)

tk.Label(input_frame, text="Enter Word:", bg='#f0f0f0').grid(row=0, column=0, sticky='w')
word_entry = tk.Entry(input_frame, width=15, validate="key", validatecommand=(validate_alpha, '%P'))
word_entry.grid(row=0, column=1, padx=5)

tk.Label(input_frame, text="Row (1-15):", bg='#f0f0f0').grid(row=1, column=0, sticky='w')
row_entry = tk.Entry(input_frame, width=5)
row_entry.grid(row=1, column=1, padx=5, sticky='w')

tk.Label(input_frame, text="Column (1-15):", bg='#f0f0f0').grid(row=2, column=0, sticky='w')
col_entry = tk.Entry(input_frame, width=5)
col_entry.grid(row=2, column=1, padx=5, sticky='w')

tk.Label(input_frame, text="Direction:", bg='#f0f0f0').grid(row=3, column=0, sticky='w')
direction_var = tk.StringVar(value="horizontal")
tk.Radiobutton(input_frame, text="Horizontal", variable=direction_var, value="horizontal", bg='#f0f0f0').grid(row=3, column=1, sticky='w')
tk.Radiobutton(input_frame, text="Vertical", variable=direction_var, value="vertical", bg='#f0f0f0').grid(row=4, column=1, sticky='w')

place_button = tk.Button(input_frame, text="Place Word", command=place_word)
place_button.grid(row=5, column=0, columnspan=2, pady=5)

skip_button = tk.Button(input_frame, text="Skip Turn", command=skip_turn)
skip_button.grid(row=6, column=0, columnspan=2, pady=5)

history_label = tk.Label(right_panel, text="Word History:", bg='#f0f0f0', font=('Arial', 10, 'bold'))
history_label.pack(pady=(20, 5))

history_text = tk.Text(right_panel, width=30, height=15, state=tk.DISABLED)
history_text.pack()

update_racks()
update_scores()

window.mainloop()