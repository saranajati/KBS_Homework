from Bfs.engine_moves_bfs import BridgePuzzleSolverMovesBfs
from Bfs.engine_constraints_bfs import BridgePuzzleSolverConstraintsBfs


class BridgePuzzleSolverBfs(
    BridgePuzzleSolverMovesBfs, BridgePuzzleSolverConstraintsBfs
):
    def print_final_summary(self):
        print(f"\n{'='*80}")
        print(f"FINAL SUMMARY: {len(self.solutions)} SOLUTION(S) FOUND")
        print("=" * 80)

        self.solutions and self._print_solutions() or self._print_no_solutions()

        print("=" * 80)

    def _print_solutions(self):
        for i, sol in enumerate(self.solutions, 1):
            print(f"\nSolution {i}: {sol['total_time']} minutes")
            for j, (action, people, time_taken) in enumerate(sol["moves"], 1):
                action_handlers = {
                    "cross": lambda: print(
                        f"  Step {j}: {people[0]} and {people[1]} cross → {time_taken} min"
                    ),
                    "return": lambda: print(
                        f"  Step {j}: {people[0]} returns → {time_taken} min"
                    ),
                }
                handler = action_handlers.get(
                    action,
                    lambda: print(
                        f"  Step {j}: {people[0]} returns → {time_taken} min"
                    ),
                )
                handler()

    def _print_no_solutions(self):
        print("No solutions found within the time limit.")
