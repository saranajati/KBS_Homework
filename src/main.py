from facts import *


class BridgePuzzleRunner:
    def __init__(self):
        self.travel_time = [
            ("You", 1),
            ("Lab Assistant", 2),
            ("Worker", 5),
            ("Scientist", 10),
        ]
        self.max_time = 17

    def run(self):
        strategy = input("Choose search strategy (bfs/dfs): ").strip().lower()

        if strategy == "bfs":
            from Bfs.engine_bfs import BridgePuzzleSolverBfs as Solver
        else:
            from Dfs.engine import BridgePuzzleSolver as Solver

        engine = Solver(self.travel_time, self.max_time)
        engine.reset()
        engine.run()


runner = BridgePuzzleRunner()
runner.run()
