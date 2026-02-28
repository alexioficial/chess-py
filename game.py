import copy
from pieces import Pawn, Knight, Bishop, Rook, Queen, King, WHITE, BLACK


class Game:
    def __init__(self):
        self.board = [[None for _ in range(8)] for _ in range(8)]
        self.turn = WHITE
        self.en_passant_target = None  # (r, c) or None
        self.setup_board()
        self.message = ""

    def to_dict(self):
        board_state = []
        for r in range(8):
            row = []
            for c in range(8):
                p = self.board[r][c]
                row.append(p.serialize() if p else None)
            board_state.append(row)

        return {
            "board": board_state,
            "turn": self.turn,
            "en_passant_target": self.en_passant_target,
            "message": self.message,
        }

    @classmethod
    def from_dict(cls, data):
        g = cls()
        g.turn = data["turn"]
        g.en_passant_target = (
            tuple(data["en_passant_target"]) if data.get("en_passant_target") else None
        )
        g.message = data.get("message", "")

        piece_classes = {
            "Pawn": Pawn,
            "Knight": Knight,
            "Bishop": Bishop,
            "Rook": Rook,
            "Queen": Queen,
            "King": King,
        }

        for r in range(8):
            for c in range(8):
                p_data = data["board"][r][c]
                if p_data:
                    p_class = piece_classes[p_data["type"]]
                    piece = p_class(p_data["color"])
                    piece.has_moved = p_data["has_moved"]
                    g.board[r][c] = piece
                else:
                    g.board[r][c] = None
        return g

    def setup_board(self):
        # Pawns
        for c in range(8):
            self.board[1][c] = Pawn(BLACK)
            self.board[6][c] = Pawn(WHITE)

        # Pieces
        placement = [Rook, Knight, Bishop, Queen, King, Bishop, Knight, Rook]
        for c in range(8):
            self.board[0][c] = placement[c](BLACK)
            self.board[7][c] = placement[c](WHITE)

    def print_board(self):
        print("\n  a b c d e f g h")
        print("  ---------------")
        for r in range(8):
            row_str = f"{8 - r}|"
            for c in range(8):
                piece = self.board[r][c]
                if piece is None:
                    row_str += ". "
                else:
                    row_str += str(piece) + " "
            row_str += f"|{8 - r}"
            print(row_str)
        print("  ---------------")
        print("  a b c d e f g h\n")

    def get_piece(self, r, c):
        if 0 <= r < 8 and 0 <= c < 8:
            return self.board[r][c]
        return None

    def find_king(self, color):
        for r in range(8):
            for c in range(8):
                p = self.board[r][c]
                if p is not None and isinstance(p, King) and p.color == color:
                    return (r, c)
        return None

    def is_in_check(self, color):
        king_pos = self.find_king(color)
        if not king_pos:
            return False

        opp_color = BLACK if color == WHITE else WHITE
        for r in range(8):
            for c in range(8):
                p = self.board[r][c]
                if p is not None and p.color == opp_color:
                    moves = p.get_pseudo_legal_moves(self.board, r, c)
                    if king_pos in moves:
                        return True
        return False

    def is_legal_move(self, start, end):
        r1, c1 = start
        r2, c2 = end
        piece = self.board[r1][c1]

        if piece is None or piece.color != self.turn:
            return False

        moves = piece.get_pseudo_legal_moves(self.board, r1, c1)

        # Castling pseudo-legal check
        if isinstance(piece, King):
            moves.extend(self.get_castling_moves(r1, c1))

        # En passant pseudo-legal check
        if isinstance(piece, Pawn) and self.en_passant_target is not None:
            if (r2, c2) == self.en_passant_target:
                # If moving diagonally to the target
                if abs(c2 - c1) == 1 and r2 == (r1 + piece.direction):
                    moves.append((r2, c2))

        if end not in moves:
            return False

        # Make a temporary move to see if it leaves king in check
        board_copy = copy.deepcopy(self.board)
        en_passant_copy = self.en_passant_target

        # Simulate move
        self._apply_move_internal(start, end, simulate=True)
        in_check = self.is_in_check(self.turn)

        # Restore state
        self.board = board_copy
        self.en_passant_target = en_passant_copy

        return not in_check

    def get_castling_moves(self, r, c):
        moves = []
        piece = self.board[r][c]
        if not isinstance(piece, King) or piece.has_moved:
            return moves

        if self.is_in_check(self.turn):
            return moves

        # Kingside
        if isinstance(self.board[r][7], Rook) and not self.board[r][7].has_moved:
            if self.board[r][5] is None and self.board[r][6] is None:
                # Check if passing through check
                if self.is_square_safe_for_king(r, 5) and self.is_square_safe_for_king(
                    r, 6
                ):
                    moves.append((r, 6))

        # Queenside
        if isinstance(self.board[r][0], Rook) and not self.board[r][0].has_moved:
            if (
                self.board[r][1] is None
                and self.board[r][2] is None
                and self.board[r][3] is None
            ):
                # Check if passing through check
                if self.is_square_safe_for_king(r, 2) and self.is_square_safe_for_king(
                    r, 3
                ):
                    moves.append((r, 2))

        return moves

    def is_square_safe_for_king(self, target_r, target_c):
        # Check if the square is guarded by any opponent
        opp_color = BLACK if self.turn == WHITE else WHITE
        for r in range(8):
            for c in range(8):
                p = self.board[r][c]
                if p is not None and p.color == opp_color:
                    # Kings can't move pseudo-legally into another king's radius
                    if isinstance(p, King):
                        if abs(r - target_r) <= 1 and abs(c - target_c) <= 1:
                            return False
                    else:
                        moves = p.get_pseudo_legal_moves(self.board, r, c)
                        if (target_r, target_c) in moves:
                            return False
        return True

    def get_all_legal_moves(self, color):
        legal_moves = []
        for r in range(8):
            for c in range(8):
                piece = self.board[r][c]
                if piece is not None and piece.color == color:
                    pseudo_moves = piece.get_pseudo_legal_moves(self.board, r, c)
                    if isinstance(piece, King):
                        pseudo_moves.extend(self.get_castling_moves(r, c))

                    for move in pseudo_moves:
                        if self.is_legal_move((r, c), move):
                            legal_moves.append(((r, c), move))

                    # En passant
                    if isinstance(piece, Pawn) and self.en_passant_target:
                        er, ec = self.en_passant_target
                        if abs(ec - c) == 1 and er == (r + piece.direction):
                            if self.is_legal_move((r, c), (er, ec)):
                                legal_moves.append(((r, c), (er, ec)))
        return legal_moves

    def _apply_move_internal(self, start, end, simulate=False):
        r1, c1 = start
        r2, c2 = end
        piece = self.board[r1][c1]

        # Handle En Passant capture
        if isinstance(piece, Pawn) and (r2, c2) == self.en_passant_target:
            self.board[r1][c2] = None

        # Handle Castling
        if isinstance(piece, King) and abs(c2 - c1) == 2:
            if c2 == 6:  # Kingside
                rook = self.board[r1][7]
                self.board[r1][5] = rook
                self.board[r1][7] = None
                if not simulate:
                    rook.has_moved = True
            elif c2 == 2:  # Queenside
                rook = self.board[r1][0]
                self.board[r1][3] = rook
                self.board[r1][0] = None
                if not simulate:
                    rook.has_moved = True

        # Move piece
        self.board[r2][c2] = piece
        self.board[r1][c1] = None

        # Promotion
        if isinstance(piece, Pawn) and (r2 == 0 or r2 == 7):
            self.board[r2][c2] = Queen(piece.color)

        if not simulate:
            piece.has_moved = True

            # Update En Passant target
            if isinstance(piece, Pawn) and abs(r2 - r1) == 2:
                self.en_passant_target = (r1 + piece.direction, c1)
            else:
                self.en_passant_target = None

    def make_move(self, start, end):
        if not self.is_legal_move(start, end):
            self.message = "Illegal move!"
            return False

        self._apply_move_internal(start, end)

        # Turn swap
        self.turn = BLACK if self.turn == WHITE else WHITE
        self.message = ""

        # Check for Check / Checkmate / Stalemate
        moves = self.get_all_legal_moves(self.turn)
        if self.is_in_check(self.turn):
            if not moves:
                winner = "WHITE" if self.turn == BLACK else "BLACK"
                self.message = f"Checkmate! {winner} wins."
            else:
                self.message = "Check!"
        else:
            if not moves:
                self.message = "Stalemate! It's a draw."

        return True
