document.addEventListener('DOMContentLoaded', () => {
    const socket = io();
    const boardEl = document.getElementById('chessboard');
    const statusEl = document.getElementById('game-status');

    let gameState = null;
    let selectedPos = null;

    // Connect and Join Room
    socket.on('connect', () => {
        socket.emit('join', { room: ROOM_ID });
    });

    socket.on('game_started', (data) => {
        // Someone joined
        statusEl.textContent = "Game in progress";
        if (data.player_black) {
            // In a real app we'd update DOM or just reload
            window.location.reload();
        }
    });

    socket.on('update_board', (data) => {
        gameState = data;
        renderBoard(data);
        if (data.message) {
            statusEl.textContent = data.message;
        } else {
            statusEl.textContent = `${data.turn.charAt(0).toUpperCase() + data.turn.slice(1)}'s turn`;
        }
        selectedPos = null; // Clear selection on update
    });

    socket.on('game_message', (data) => {
        statusEl.textContent = data.msg;
    });

    socket.on('error', (data) => {
        console.warn("Invalid action:", data.msg);
        statusEl.textContent = `Invalid: ${data.msg}`;
        setTimeout(() => {
            if (gameState) {
                statusEl.textContent = `${gameState.turn.charAt(0).toUpperCase() + gameState.turn.slice(1)}'s turn`;
            }
        }, 2000);
        selectedPos = null;
        renderBoard(gameState);
    });

    // Helper: Map Piece class names to unicode
    const symbolMap = {
        'white': { 'Pawn': '♙', 'Knight': '♘', 'Bishop': '♗', 'Rook': '♖', 'Queen': '♕', 'King': '♔' },
        'black': { 'Pawn': '♟', 'Knight': '♞', 'Bishop': '♝', 'Rook': '♜', 'Queen': '♛', 'King': '♚' }
    };

    function renderBoard(state) {
        if (!state || !state.board) return;
        boardEl.innerHTML = ''; // Clear prev

        // Determine orientation based on player
        let isFlipped = false;
        if (CURRENT_USER === PLAYER_BLACK && CURRENT_USER !== PLAYER_WHITE) {
            isFlipped = true;
        }

        const rows = isFlipped ? [7, 6, 5, 4, 3, 2, 1, 0] : [0, 1, 2, 3, 4, 5, 6, 7];

        for (let r of rows) {
            const cols = isFlipped ? [7, 6, 5, 4, 3, 2, 1, 0] : [0, 1, 2, 3, 4, 5, 6, 7];
            for (let c of cols) {
                const square = document.createElement('div');
                square.classList.add('square');
                const isLight = (r + c) % 2 === 0;
                square.classList.add(isLight ? 'light' : 'dark');

                square.dataset.r = r;
                square.dataset.c = c;

                if (selectedPos && selectedPos.r === r && selectedPos.c === c) {
                    square.classList.add('selected');
                }

                const pieceData = state.board[r][c];
                if (pieceData) {
                    const symbol = symbolMap[pieceData.color][pieceData.type] || '?';
                    const pieceSpan = document.createElement('span');
                    pieceSpan.classList.add('piece');
                    pieceSpan.classList.add(`${pieceData.color}-piece`);
                    pieceSpan.textContent = symbol;
                    square.appendChild(pieceSpan);
                }

                // Interaction
                if (!IS_SPECTATOR) {
                    square.addEventListener('click', () => handleSquareClick(r, c, pieceData));
                }

                boardEl.appendChild(square);
            }
        }
    }

    function handleSquareClick(r, c, pieceData) {
        if (!gameState) return;

        // If not player's turn, ignore
        const userColor = CURRENT_USER === PLAYER_WHITE ? 'white' : 'black';
        if (gameState.turn !== userColor) {
            statusEl.textContent = "Wait for your turn!";
            return;
        }

        if (selectedPos) {
            // Already selected, try moving
            if (selectedPos.r === r && selectedPos.c === c) {
                // Deselect
                selectedPos = null;
                renderBoard(gameState);
            } else {
                // Emit move
                socket.emit('make_move', {
                    room: ROOM_ID,
                    start: [selectedPos.r, selectedPos.c],
                    end: [r, c]
                });
                selectedPos = null; // Awaiting response
            }
        } else {
            // Select piece (only if it matches user color)
            if (pieceData && pieceData.color === userColor) {
                selectedPos = { r, c };
                renderBoard(gameState);
            }
        }
    }

});
