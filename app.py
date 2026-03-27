from flask import Flask, render_template, request, jsonify, session
from flask_cors import CORS
import chess
import os
from dotenv import load_dotenv
from game_logic import (
    create_new_game, get_board_state,
    make_move, get_ai_move, get_board_svg, get_result
)
from gemini_helper import (
    get_move_commentary, get_move_suggestion,
    get_game_summary, get_hint
)

load_dotenv()

app = Flask(__name__)
app.secret_key = os.urandom(24)
CORS(app)

# Store board in memory (simple approach for single user)
game_boards = {}

@app.route("/")
def index():
    """Serve the main game page."""
    return render_template("index.html")

@app.route("/api/new-game", methods=["POST"])
def new_game():
    """Start a new chess game."""
    session_id = request.json.get("session_id", "default")
    board = create_new_game()
    game_boards[session_id] = board
    
    state = get_board_state(board)
    svg = get_board_svg(board)
    
    return jsonify({
        "success": True,
        "board_svg": svg,
        "state": state,
        "message": "New game started! You play as White. Good luck! ♟️"
    })

@app.route("/api/move", methods=["POST"])
def player_move():
    """Handle player's move, then AI responds."""
    data = request.json
    session_id = data.get("session_id", "default")
    move_uci = data.get("move", "")
    
    board = game_boards.get(session_id)
    if not board:
        return jsonify({"success": False, "error": "No active game. Start a new game!"})
    
    # Make player's move
    success, error = make_move(board, move_uci)
    if not success:
        return jsonify({"success": False, "error": error})
    
    player_color = "white"  # Player is always white
    state = get_board_state(board)
    
    # Get Gemini commentary on player's move
    commentary = get_move_commentary(board.fen(), move_uci, player_color)
    
    response_data = {
        "success": True,
        "board_svg": get_board_svg(board),
        "state": state,
        "commentary": commentary,
        "ai_move": None
    }
    
    # If game not over, AI makes its move
    if not state["is_game_over"]:
        ai_move = get_ai_move(board)
        if ai_move:
            state = get_board_state(board)
            ai_commentary = get_move_commentary(board.fen(), ai_move, "black")
            
            response_data.update({
                "board_svg": get_board_svg(board),
                "state": state,
                "ai_move": ai_move,
                "ai_commentary": ai_commentary
            })
    
    # Check if game ended
    if state["is_game_over"]:
        result = get_result(board)
        summary = get_game_summary(board.fen(), result, state["move_count"])
        response_data["game_over"] = True
        response_data["result"] = result
        response_data["summary"] = summary
    
    return jsonify(response_data)

@app.route("/api/hint", methods=["POST"])
def get_hint_route():
    """Give player a Gemini-powered hint."""
    data = request.json
    session_id = data.get("session_id", "default")
    board = game_boards.get(session_id)
    
    if not board:
        return jsonify({"success": False, "error": "No active game!"})
    
    hint = get_hint(board.fen(), "white")
    return jsonify({"success": True, "hint": hint})

@app.route("/api/suggest", methods=["POST"])
def suggest_move():
    """Gemini suggests the best move."""
    data = request.json
    session_id = data.get("session_id", "default")
    board = game_boards.get(session_id)
    
    if not board:
        return jsonify({"success": False, "error": "No active game!"})
    
    suggestion = get_move_suggestion(board.fen(), "white")
    return jsonify({"success": True, "suggestion": suggestion})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port, debug=False)