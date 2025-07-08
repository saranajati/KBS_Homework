from engine_moves import BridgePuzzleSolverMoves
from engine_constraints import BridgePuzzleSolverConstraints

class BridgePuzzleSolver(BridgePuzzleSolverMoves, BridgePuzzleSolverConstraints):
   def print_final_summary(self):
    print(f"\n{'='*80}")
    print(f"FINAL SUMMARY: {len(self.solutions)} SOLUTION(S) FOUND")
    print("=" * 80)
    [print(f"\nSolution {i}: {sol['total_time']} minutes") or
     [print(f"  Step {j}: {people[0]} and {people[1]} cross → {time_taken} min") if action == "cross"
      else print(f"  Step {j}: {people[0]} returns → {time_taken} min")
      for j, (action, people, time_taken) in enumerate(reversed(sol['moves']), 1)]
     for i, sol in enumerate(self.solutions, 1)] or print("No solutions found within the time limit.")
    print("=" * 80)
