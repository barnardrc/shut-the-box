import numpy as np
import itertools

def get_roll(current_board):
    """
    Standard Shut the Box rules: 
    If sum of remaining numbers <= 6, roll 1 die. Else roll 2.
    """
    if sum(current_board) <= 6:
        return np.random.randint(1, 7)
    else:
        return np.random.randint(1, 7) + np.random.randint(1, 7)

def find_valid_moves(target_sum, available_nums):
    """
    Finds all combinations of available numbers that add up to target_sum.
    Returns a list of tuples. e.g. [(9), (5, 4), (1, 2, 6)]
    """
    valid_moves = []
    for r in range(1, len(available_nums) + 1):
        for combo in itertools.combinations(available_nums, r):
            if sum(combo) == target_sum:
                valid_moves.append(combo)
    return valid_moves

def count_ways_to_make_target(board, target):
    """
    Returns the number of unique combinations in 'board' that sum to 'target'.
    """
    count = 0
    # Only check combinations up to length 4 
    for r in range(1, min(len(board) + 1, 5)): 
        for combo in itertools.combinations(board, r):
            if sum(combo) == target:
                count += 1
    return count

def select_move(moves, strategy_name, current_board):
    """
    Filters the list of valid moves based on the selected strategy.
    Returns the 'best' tuple to flip.
    """
    if not moves:
        return None

    # 1. Largest numbers picked first (Maximize the single largest value in the combo)
    if strategy_name == "largest_val":
        # Sort by max value in combo (descending), then by length
        return sorted(moves, key=lambda x: (max(x), len(x)), reverse=True)[0]

    # 2. Smallest numbers picked first (Prioritize removing small numbers)
    elif strategy_name == "smallest_val":
        # Sort by min value in combo (ascending)
        return sorted(moves, key=lambda x: min(x))[0]

    # 3. Highest Ranges (Max value - Min value is largest)
    elif strategy_name == "highest_range":
        return sorted(moves, key=lambda x: max(x) - min(x), reverse=True)[0]
        
    # 4. Lowest Ranges (Max value - Min value is smallest)
    elif strategy_name == "lowest_range":
        return sorted(moves, key=lambda x: max(x) - min(x))[0]

    # 5. Least amount of numbers (Prefer [9] over [4, 5])
    elif strategy_name == "min_count":
        return sorted(moves, key=len)[0]

    # 6. Most amount of numbers (Prefer [1, 2, 6] over [9])
    elif strategy_name == "max_count":
        return sorted(moves, key=len, reverse=True)[0]
    
    elif strategy_name == "composite1":
        # 1. Largest Number First (max(x))
        # 2. Min amount of numbers (len(x)) -> denoted by -len(x) for descending sort
        # 3. Largest Range (max(x) - min(x))
        return sorted(moves, key=lambda x: (max(x), -len(x), max(x) - min(x)), reverse=True)[0]
    
    elif strategy_name == "composite2":
        # 1. Minimum amount of numbers
        # 2. Largest Range next
        return sorted(moves, key=lambda x: (-len(x), max(x) - min(x)), reverse=True)[0]
    
    elif strategy_name == "preserve_7s":
        def score_move(move):
            future_board = [x for x in current_board if x not in move]
            
            # Count how many ways the future board can make 7
            sevens_count = count_ways_to_make_target(future_board, 7)

            return (sevens_count, -len(move), max(move))

        # Descending sort for highest 7s count
        return sorted(moves, key=score_move, reverse=True)[0]
    
    if strategy_name == "composite2_with_7s":
        
        def score_move(move):
            # Create future board
            future_board = [x for x in current_board if x not in move]
            
            # How many ways can we make 7?
            sevens_count = count_ways_to_make_target(future_board, 7)

            length_score = -len(move)

            range_score = max(move) - min(move)
            
            return (sevens_count, length_score, range_score)

        return sorted(moves, key=score_move, reverse=True)[0]
    
    if strategy_name == "composite2_with_7s_2nd":
        
        def score_move(move):
            future_board = [x for x in current_board if x not in move]
            
            sevens_count = count_ways_to_make_target(future_board, 7)
            
            length_score = -len(move)
            
            range_score = max(move) - min(move)
            
            return (length_score, sevens_count, range_score)

        return sorted(moves, key=score_move, reverse=True)[0]
    
    if strategy_name == "composite2_with_7s_3rd":
        
        def score_move(move):
            future_board = [x for x in current_board if x not in move]
            
            sevens_count = count_ways_to_make_target(future_board, 7)
            
            length_score = -len(move)

            range_score = max(move) - min(move)
            
            return (length_score, range_score, sevens_count)

        return sorted(moves, key=score_move, reverse=True)[0]
    
    return moves[0]

def play_game(strategy_name, verbose=False):
    board = [1, 2, 3, 4, 5, 6, 7, 8, 9]
    
    while board:
        roll = get_roll(board)
        moves = find_valid_moves(roll, board)
        
        if not moves:
            if verbose: print(f"Game Over! Rolled {roll}, Board: {board}")
            break
            
        chosen_move = select_move(moves, strategy_name, board)
        
        if verbose: 
            print(f"Rolled {roll} | Board {board} | Moves {moves} | Chose {chosen_move}")
            
        for num in chosen_move:
            board.remove(num)

    return sum(board)

def run_simulation():
    strategies = [
        "largest_val", 
        "lowest_range", 
        "min_count", "composite1",
        "composite2", "preserve_7s",
        "composite2_with_7s", "composite2_with_7s_2nd",
        "composite2_with_7s_3rd"
    ]
    
    amt_sims = 1000  # Number of "sessions" to run
    rounds_per_sim = 10 # Number of games per session
    
    print(f"{'STRATEGY':<20} | {'AVG 10-GAME TOTAL':<20} | {'AVG PER GAME':<15}")
    print("-" * 65)
    
    for strat in strategies:
        session_totals = []
        
        for _ in range(amt_sims):
            current_session_score = 0
            
            for _ in range(rounds_per_sim):
                current_session_score += play_game(strat)
            
            session_totals.append(current_session_score)
        
        # Calculate statistics
        avg_session = np.mean(session_totals)
        avg_game = avg_session / rounds_per_sim
        
        print(f"{strat:<20} | {avg_session:<20.2f} | {avg_game:<15.2f}")

if __name__ == "__main__":
    # np.random.seed(43)
    # Test a single game with verbosity to see logic working
    # play_game("highest_range", verbose=True)
    # print('-'*50)
    # play_game("min_count", verbose=True)
    
    # Run the full suite
    run_simulation()