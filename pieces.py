WHITE = "white"
BLACK = "black"


class Piece:
    def __init__(self, color):
        self.color = color
        self.has_moved = False
        self.symbol = "?"

    def __str__(self):
        return self.symbol

    def get_pseudo_legal_moves(self, board, r, c):
        """
        Returns a list of (row, col) moves.
        `board` is an 8x8 list of Piece objects or None.
        Pseudo-legal means it ignores whether the king is left in check.
        """
        return []

    def get_sliding_moves(self, board, r, c, directions):
        moves = []
        for dr, dc in directions:
            nr, nc = r + dr, c + dc
            while 0 <= nr < 8 and 0 <= nc < 8:
                target = board[nr][nc]
                if target is None:
                    moves.append((nr, nc))
                elif target.color != self.color:
                    moves.append((nr, nc))
                    break
                else:
                    break
                nr += dr
                nc += dc
        return moves


class Pawn(Piece):
    def __init__(self, color):
        super().__init__(color)
        self.symbol = "♙" if color == WHITE else "♟"
        self.direction = -1 if color == WHITE else 1

    def get_pseudo_legal_moves(self, board, r, c):
        moves = []

        # Forward 1
        nr = r + self.direction
        if 0 <= nr < 8 and board[nr][c] is None:
            moves.append((nr, c))
            # Forward 2
            if not self.has_moved:
                nr2 = r + 2 * self.direction
                if 0 <= nr2 < 8 and board[nr2][c] is None:
                    moves.append((nr2, c))

        # Captures
        for dc in [-1, 1]:
            nc = c + dc
            if 0 <= nr < 8 and 0 <= nc < 8:
                target = board[nr][nc]
                if target is not None and target.color != self.color:
                    moves.append((nr, nc))

        return moves


class Knight(Piece):
    def __init__(self, color):
        super().__init__(color)
        self.symbol = "♘" if color == WHITE else "♞"

    def get_pseudo_legal_moves(self, board, r, c):
        moves = []
        offsets = [
            (-2, -1),
            (-2, 1),
            (-1, -2),
            (-1, 2),
            (1, -2),
            (1, 2),
            (2, -1),
            (2, 1),
        ]
        for dr, dc in offsets:
            nr, nc = r + dr, c + dc
            if 0 <= nr < 8 and 0 <= nc < 8:
                target = board[nr][nc]
                if target is None or target.color != self.color:
                    moves.append((nr, nc))
        return moves


class Bishop(Piece):
    def __init__(self, color):
        super().__init__(color)
        self.symbol = "♗" if color == WHITE else "♝"
        self.directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]

    def get_pseudo_legal_moves(self, board, r, c):
        return self.get_sliding_moves(board, r, c, self.directions)


class Rook(Piece):
    def __init__(self, color):
        super().__init__(color)
        self.symbol = "♖" if color == WHITE else "♜"
        self.directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    def get_pseudo_legal_moves(self, board, r, c):
        return self.get_sliding_moves(board, r, c, self.directions)


class Queen(Piece):
    def __init__(self, color):
        super().__init__(color)
        self.symbol = "♕" if color == WHITE else "♛"
        self.directions = [
            (-1, -1),
            (-1, 1),
            (1, -1),
            (1, 1),
            (-1, 0),
            (1, 0),
            (0, -1),
            (0, 1),
        ]

    def get_pseudo_legal_moves(self, board, r, c):
        return self.get_sliding_moves(board, r, c, self.directions)


class King(Piece):
    def __init__(self, color):
        super().__init__(color)
        self.symbol = "♔" if color == WHITE else "♚"

    def get_pseudo_legal_moves(self, board, r, c):
        moves = []
        directions = [
            (-1, -1),
            (-1, 1),
            (1, -1),
            (1, 1),
            (-1, 0),
            (1, 0),
            (0, -1),
            (0, 1),
        ]
        for dr, dc in directions:
            nr, nc = r + dr, c + dc
            if 0 <= nr < 8 and 0 <= nc < 8:
                target = board[nr][nc]
                if target is None or target.color != self.color:
                    moves.append((nr, nc))
        return moves
