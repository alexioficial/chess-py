from game import Game
from pieces import WHITE


def parse_move(move_str):
    move_str = move_str.strip().lower()
    if len(move_str) != 4:
        return None

    try:
        r1 = 8 - int(move_str[1])
        c1 = ord(move_str[0]) - ord("a")
        r2 = 8 - int(move_str[3])
        c2 = ord(move_str[2]) - ord("a")

        if 0 <= r1 < 8 and 0 <= c1 < 8 and 0 <= r2 < 8 and 0 <= c2 < 8:
            return ((r1, c1), (r2, c2))
    except ValueError:
        pass

    return None


def main():
    game = Game()

    print("Welcome to Python Chess!")
    print("Commands:")
    print(" - 'e2e4': Move piece from e2 to e4")
    print(" - 'quit' or 'exit': Quit game")

    while True:
        game.print_board()

        if game.message:
            print("==>", game.message)
            if "wins" in game.message or "draw" in game.message:
                break
            if "Check!" not in game.message:
                game.message = ""

        turn_str = "White's turn" if game.turn == WHITE else "Black's turn"
        try:
            user_input = input(f"{turn_str} > ")
        except (KeyboardInterrupt, EOFError):
            print("\nExiting...")
            break

        if user_input.lower() in ("quit", "exit"):
            break

        move = parse_move(user_input)
        if move:
            start, end = move
            _success = game.make_move(start, end)
        else:
            game.message = "Invalid format! Use e.g. 'e2e4'"


if __name__ == "__main__":
    main()
