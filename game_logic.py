import chess
import chess.svg

def create_new_game():
    """Start a fresh chess game."""
    board = chess.Board()
    return board

def get_board_state(board):
    """Return board info as a dictionary."""
    return {
        "fen": board.fen(),
        "turn": "white" if board.turn == chess.WHITE else "black",
        "is_check": board.is_check(),
        "is_checkmate": board.is_checkmate(),
        "is_stalemate": board.is_stalemate(),
        "is_game_over": board.is_game_over(),
        "legal_moves": [move.uci() for move in board.legal_moves],
        "move_count": board.fullmove_number
    }

def make_move(board, move_uci):
    """
    Attempt to make a move on the board.
    move_uci: move in UCI format e.g. "e2e4"
    Returns: (success, error_message)
    """
    try:
        move = chess.Move.from_uci(move_uci)
        if move in board.legal_moves:
            board.push(move)
            return True, None
        else:
            return False, "Illegal move! Try again."
    except Exception as e:
        return False, f"Invalid move format: {str(e)}"

def get_ai_move(board):
    """
    Simple AI: picks a random legal move.
    (Gemini will enhance this with suggestions)
    """
    import random
    legal_moves = list(board.legal_moves)
    if legal_moves:
        move = random.choice(legal_moves)
        board.push(move)
        return move.uci()
    return None

def get_board_svg(board):
    """Returns board as SVG for display."""
    return chess.svg.board(board=board, size=400)

def get_result(board):
    """Get game result string."""
    if board.is_checkmate():
        winner = "Black" if board.turn == chess.WHITE else "White"
        return f"{winner} wins by Checkmate!"
    elif board.is_stalemate():
        return "Draw by Stalemate!"
    elif board.is_insufficient_material():
        return "Draw by Insufficient Material!"
    return "Game Over"