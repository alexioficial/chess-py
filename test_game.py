from game import Game


def run_tests():
    print("Testing Game Initialization...")
    g = Game()
    g.print_board()

    print("Testing e2e4 (White Pawn Push)...")
    res1 = g.make_move((6, 4), (4, 4))
    print("Move e2e4 success:", res1)
    g.print_board()

    print("Testing e7e5 (Black Pawn Push)...")
    res2 = g.make_move((1, 4), (3, 4))
    print("Move e7e5 success:", res2)
    g.print_board()

    print("Testing g1f3 (White Knight)...")
    res3 = g.make_move((7, 6), (5, 5))
    print("Move g1f3 success:", res3)
    g.print_board()

    print("Testing invalid move (e1e2 White King into blocked square)...")
    res4 = g.make_move((7, 4), (6, 4))
    print("Move e1e2 success:", res4)  # Should be False since it's blocked

    if res1 and res2 and res3 and not res4:
        print("All basic movement tests PASS!")
    else:
        print("Some basic movement tests FAIL!")


if __name__ == "__main__":
    run_tests()
