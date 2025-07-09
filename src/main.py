from facts import *


def main():
    print("BRIDGE PUZZLE (KBS Homework)")
    print("-" * 100)

    travel_time = [("You", 1), ("Lab Assistant", 2), ("Worker", 5), ("Scientist", 10)]
    max_time = 17

    strategy = input("Choose search strategy (bfs/dfs): ").strip().lower()

    if strategy == "bfs":
        from Bfs.engine_bfs import BridgePuzzleSolverBfs as Solver
    else:
        from Dfs.engine import BridgePuzzleSolver as Solver

    engine = Solver(travel_time, max_time)
    engine.reset()
    engine.run()


if __name__ == "__main__":
    main()
