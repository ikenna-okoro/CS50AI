"""
Tic Tac Toe Player
"""

import math, copy

X = "X"
O = "O"
EMPTY = None


def initial_state():
    """
    Returns starting state of the board.
    """
    return [[EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY]]


def player(board):
    """
    Returns player who has the next turn on a board.
    """
    # Flatten the 2D list into a single list
    flat = [cell for row in board for cell in row]
    
    x_count = flat.count(X)
    o_count = flat.count(O)
    
    # Rule: X always goes first
    if x_count <= o_count:
        return X
    else:
        return O


def actions(board):
    """
    Returns set of all possible actions (i, j) available on the board.
    """
    legal_moves = set()
    for i in range(3):
        for j in range(3):
            if board[i][j] == EMPTY:
                legal_moves.add((i, j))
    return legal_moves


def result(board, action):
    """
    Returns the board that results from making move (i, j) on the board.
    """
    r, c = action
    if r not in range(3) or c not in range(3):
        raise ValueError("Index out of Bounds")
    
    # Ensure the action is valid
    if board[r][c] != EMPTY:
        raise ValueError("Invalid action: cell is not empty.")
    
    # Deep copy the state so we don't modify the original
    new_state = copy.deepcopy(board)

    # Determine whose turn it is and apply the move
    current = player(board)
    new_state[r][c] = current
    
    return new_state


def winner(board):
    """
    Returns the winner of the game, if there is one.
    """
    # Check rows
    for row in board:
        if row[0] == row[1] == row[2] != EMPTY:
            return row[0]

    # Check columns
    for col in range(3):
        if board[0][col] == board[1][col] == board[2][col] != EMPTY:
            return board[0][col]

    # Check diagonals
    if board[0][0] == board[1][1] == board[2][2] != EMPTY:
        return board[0][0]
    if board[0][2] == board[1][1] == board[2][0] != EMPTY:
        return board[0][2]
    return None


def terminal(board):
    """
    Returns True if game is over, False otherwise.
    """
    return winner(board) is not None or all(cell != EMPTY for row in board for cell in row)


def utility(board):
    """
    Returns 1 if X has won the game, -1 if O has won, 0 otherwise.
    """
    if terminal(board):
        win = winner(board)
        if win == X:
            return 1
        elif win == O:
            return -1
        return 0


def immediate_winning_moves(board, player_symbol):
    """
    Returns a set of action (coordinate) where if the player plays (X or O) would win immediately
    by playing that action on the board.
    """
    wins = set()
    for action in actions(board):
        r, c = action
        # simulate move
        new = copy.deepcopy(board)
        if new[r][c] != EMPTY:
            raise ValueError("Invalid action")
        new[r][c] = player_symbol
        if winner(new) == player_symbol:
            wins.add(action)
    return wins


def minimax(board):
    """
    Returns the optimal action for the current player on the board.
    """
    if terminal(board):
        return None # no moves left    
    # Determine whose turn it is to play
    current = player(board)

    # X's turn (maximizes score)
    if current == X:
        # If the opponent (O) has an immediate winning move next turn,
        # X should block it now.
        opp_wins = immediate_winning_moves(board, O)
        if opp_wins:
            # if there's a blocking move, return it (if multiple, any is fine)
            for a in actions(board):
                if a in opp_wins:
                    return a
        v = float("-inf")
        optimal_move = None
        for action in actions(board):
            val = min_value_ab(result(board, action), v, float("inf"))
            if val > v:
                v = val
                optimal_move = action
                # short-circuit if we found a winning move
                if v == 1:
                    break
        return optimal_move

    # O's turn (minimizes score)
    else:
        # If the opponent (X) has an immediate winning move next turn,
        # O should block it now.
        opp_wins = immediate_winning_moves(board, X)
        if opp_wins:
            for a in actions(board):
                if a in opp_wins:
                    return a
        v = float("inf")
        optimal_move = None
        for action in actions(board):
            val = max_value_ab(result(board, action), float("-inf"), v)
            if val < v:
                v = val
                optimal_move = action
                # short-circuit if we found a forcing winning move for O
                if v == -1:
                    break
        return optimal_move

def max_value(board):
    if terminal(board):
        return utility(board)
    v = float("-inf")
    for action in actions(board):
        v = max(v, min_value(result(board, action)))
    return v

def min_value(board):            
    if terminal(board):
        return utility(board)
    v = float("inf")
    for action in actions(board):
        v = min(v, max_value(result(board, action)))
    return v


def max_value_ab(board, alpha, beta):
    """Alpha-beta version of max_value.
    alpha: best already explored option along path to MAX
    beta: best already explored option along path to MIN
    """
    if terminal(board):
        return utility(board)
    v = float("-inf")
    for action in actions(board):
        v = max(v, min_value_ab(result(board, action), alpha, beta))
        # update alpha
        alpha = max(alpha, v)
        if alpha >= beta:
            # beta cut-off
            break
    return v


def min_value_ab(board, alpha, beta):
    """Alpha-beta version of min_value.
    alpha: best already explored option along path to MAX
    beta: best already explored option along path to MIN
    """
    if terminal(board):
        return utility(board)
    v = float("inf")
    for action in actions(board):
        v = min(v, max_value_ab(result(board, action), alpha, beta))
        # update beta
        beta = min(beta, v)
        if alpha >= beta:
            # alpha cut-off
            break
    return v


def max_value_ab_wrapper(board):
    return max_value_ab(board, float("-inf"), float("inf"))


def min_value_ab_wrapper(board):
    return min_value_ab(board, float("-inf"), float("inf"))