from dotenv import load_dotenv
load_dotenv()

import google.generativeai as genai
import os

# Configure Gemini
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-2.5-flash")

def get_move_commentary(board_fen, last_move, player_color):
    """
    Gemini commentates on the last move made.
    board_fen = current board state in FEN notation
    last_move = e.g. "e2e4"
    player_color = "white" or "black"
    """
    prompt = f"""
    You are an enthusiastic chess commentator. 
    The {player_color} player just made the move: {last_move}
    Current board position (FEN): {board_fen}
    
    Give a short, exciting 1-2 sentence commentary on this move.
    Mention if it's a good move, risky move, or brilliant move.
    Keep it fun and beginner-friendly.
    """
    response = model.generate_content(prompt)
    return response.text

def get_move_suggestion(board_fen, player_color):
    """
    Gemini suggests a good move with explanation.
    """
    prompt = f"""
    You are a friendly chess coach helping a beginner.
    Current board (FEN): {board_fen}
    It is {player_color}'s turn.
    
    Suggest ONE good move in this exact format:
    MOVE: [from_square][to_square]  (example: MOVE: e2e4)
    REASON: [one simple sentence why]
    
    Only suggest legal chess moves.
    """
    response = model.generate_content(prompt)
    return response.text

def get_game_summary(board_fen, result, move_count):
    """
    Gemini gives a fun game summary at the end.
    """
    prompt = f"""
    A chess game just ended.
    Result: {result}
    Total moves played: {move_count}
    Final board (FEN): {board_fen}
    
    Write a fun 3-4 sentence summary of this game.
    Congratulate the winner, comment on game length.
    End with a motivational tip for improvement.
    Keep it encouraging and fun!
    """
    response = model.generate_content(prompt)
    return response.text

def get_hint(board_fen, player_color):
    """
    Gives a strategic hint without revealing the exact move.
    """
    prompt = f"""
    You are a chess mentor helping a beginner.
    Current board (FEN): {board_fen}
    {player_color} is thinking about their next move.
    
    Give ONE strategic tip or thing to look for.
    Do NOT tell the exact move — just guide their thinking.
    Keep it to 1-2 sentences. Be encouraging.
    """
    response = model.generate_content(prompt)
    return response.text