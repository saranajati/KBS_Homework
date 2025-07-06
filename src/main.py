from experta import Fact
from normal_engine import BridgePuzzleSolver


def main():
    print("BRIDGE PUZZLE (KBS Homework)")
    print("-" * 100)

    travel_time = [
        ("You", 1),
        ("Lab Assistant", 2),
        ("Worker", 5),
        ("Scientist", 10)
    ]
    max_time = 17

    engine = BridgePuzzleSolver(travel_time, max_time)
    engine.reset()
    engine.run()


if __name__ == "__main__":
    main()
