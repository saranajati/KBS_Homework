from experta import Fact
from engine import BridgePuzzleSolver
from facts import *
from algorithms import *


def main():
    print("BRIDGE PUZZLE (KBS Homework)")
    print("-" * 100)

    travel_time = [("You", 1), ("Lab Assistant", 2), ("Worker", 5), ("Scientist", 10)]
    max_time = 17

    # engine = BridgePuzzleSolver(travel_time, max_time)
    # engine.reset()
    # engine.run()

    strategy_input = input("Choose search strategy (bfs / dfs): ").strip().lower()
    controller = BridgePuzzleAlgorithms(people=travel_time, max_time=max_time)
    controller.reset()
    controller.declare(SearchAlgorithm(name=strategy_input))
    controller.run()


if __name__ == "__main__":
    main()
