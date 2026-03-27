const SESSION_ID = "player_" + Math.random().toString(36).substr(2, 9);
let moveCount = 0;

async function startNewGame() {
    setCommentary("Starting new game...", true);
    document.getElementById("chess-board").innerHTML = '<p class="loading">Setting up board...</p>';

    const res = await fetch("/api/new-game", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ session_id: SESSION_ID })
    });

    const data = await res.json();
    if (data.success) {
        updateBoard(data.board_svg);
        updateStatus(data.state);
        setCommentary(data.message);
        document.getElementById("move-history").innerHTML = "";
        document.getElementById("move-btn").disabled = false;
        document.getElementById("hint-btn").disabled = false;
        document.getElementById("suggest-btn").disabled = false;
        moveCount = 0;
    }
}

async function makeMove() {
    const input = document.getElementById("move-input");
    const move = input.value.trim().toLowerCase();

    if (!move) {
        setCommentary("⚠️ Please enter a move first (e.g. e2e4)");
        return;
    }

    setCommentary("Making your move...", true);
    disableButtons(true);

    const res = await fetch("/api/move", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ session_id: SESSION_ID, move: move })
    });

    const data = await res.json();

    if (!data.success) {
        setCommentary("❌ " + data.error);
        disableButtons(false);
        return;
    }

    // Update board and status
    updateBoard(data.board_svg);
    updateStatus(data.state);
    addMoveToHistory(move, data.ai_move);
    input.value = "";

    // Show commentary
    let fullCommentary = "";
    if (data.commentary) fullCommentary += "You: " + data.commentary;
    if (data.ai_move && data.ai_commentary) {
        fullCommentary += "\n\nAI played " + data.ai_move + ": " + data.ai_commentary;
    }
    setCommentary(fullCommentary);

    // Handle game over
    if (data.game_over) {
        showGameOver(data.result, data.summary);
        disableButtons(true);
    } else {
        disableButtons(false);
    }
}

async function getHint() {
    setCommentary("Thinking of a hint for you...", true);

    const res = await fetch("/api/hint", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ session_id: SESSION_ID })
    });

    const data = await res.json();
    if (data.success) setCommentary("💡 Hint: " + data.hint);
}

async function getSuggestion() {
    setCommentary("Analyzing best move...", true);

    const res = await fetch("/api/suggest", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ session_id: SESSION_ID })
    });

    const data = await res.json();
    if (data.success) setCommentary("🤖 Suggestion:\n" + data.suggestion);
}

// ---- Helper functions ----

function updateBoard(svg) {
    document.getElementById("chess-board").innerHTML = svg;
}

function updateStatus(state) {
    const statusEl = document.getElementById("game-status");
    const turnEl = document.getElementById("turn-indicator");

    let statusText = `Move ${state.move_count} | `;
    if (state.is_check) statusText += '<span class="in-check">⚠️ CHECK!</span>';
    else statusText += "Position normal";

    statusEl.innerHTML = statusText;
    turnEl.textContent = state.turn === "white" ? "⬜ White's Turn" : "⬛ Black's Turn";
    turnEl.className = "turn " + state.turn;
}

function addMoveToHistory(playerMove, aiMove) {
    const historyEl = document.getElementById("move-history");
    moveCount++;

    const entry = document.createElement("div");
    entry.className = "move-entry";
    entry.innerHTML = `
        <span class="move-num">${moveCount}.</span>
        <span>⬜ ${playerMove}</span>
        ${aiMove ? `<span>⬛ ${aiMove}</span>` : ""}
    `;
    historyEl.prepend(entry);
}

function setCommentary(text, isLoading = false) {
    const el = document.getElementById("commentary");
    el.className = isLoading ? "loading" : "";
    el.textContent = text;
}

function showGameOver(result, summary) {
    const commentaryEl = document.getElementById("commentary");
    commentaryEl.innerHTML = `
        <div class="game-over-banner">🏆 ${result}</div>
        <br>
        <p>${summary}</p>
    `;
}

function disableButtons(disabled) {
    document.getElementById("move-btn").disabled = disabled;
    document.getElementById("hint-btn").disabled = disabled;
    document.getElementById("suggest-btn").disabled = disabled;
}

// Allow pressing Enter to submit move
document.addEventListener("DOMContentLoaded", () => {
    document.getElementById("move-input").addEventListener("keypress", (e) => {
        if (e.key === "Enter") makeMove();
    });
});