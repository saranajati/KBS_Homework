from facts import *
from experta import *
import collections
import collections.abc
collections.Mapping = collections.abc.Mapping


class BridgePuzzleSolver(KnowledgeEngine):
    def __init__(self, people, max_time=17):
        super().__init__()
        self.people = {name: float(time) for name, time in people}
        self.max_time = float(max_time)
        self.solutions = []  # Store all solutions
        self.solution_count = 0

    @Rule()
    def initialize(self):
        """Initialize with all people on left side"""
        left_side = list(self.people.keys())
        self.declare(State(
            left=left_side,
            right=[],
            flashlight_location="left",
            elapsed_time=0.0,
            path=[],
            depth=0
        ))
        self.declare(TimeConstraint(max_time=17.0))

    # Rule: Check if state is within valid time window
    @Rule(
        AS.state << State(
            elapsed_time=MATCH.elapsed_time
        ),
        TimeConstraint(max_time=MATCH.max_time),
        TEST(lambda elapsed_time, max_time: elapsed_time < max_time)
    )
    def mark_valid_time_window(self, state, elapsed_time, max_time):
        """Mark states that are within valid time window"""
        self.declare(ValidTimeWindow(
            state_ref=state,
            elapsed_time=elapsed_time
        ))

    # Rule: Check if state has sufficient people for crossing
    @Rule(
        AS.state << State(
            left=MATCH.left,
            flashlight_location="left"
        ),
        TEST(lambda left: len(left) >= 2)
    )
    def mark_sufficient_people_left(self, state, left):
        """Mark states with sufficient people on left for crossing"""
        self.declare(SufficientPeople(
            state_ref=state,
            side="left",
            count=len(left)
        ))

    # Rule: Check if state has sufficient people for returning
    @Rule(
        AS.state << State(
            left=MATCH.left,
            right=MATCH.right,
            flashlight_location="right"
        ),
        TEST(lambda right: len(right) >= 1),
        TEST(lambda left: len(left) > 0)
    )
    def mark_sufficient_people_right(self, state, left, right):
        """Mark states with sufficient people on right for returning"""
        self.declare(SufficientPeople(
            state_ref=state,
            side="right",
            count=len(right)
        ))

    # Rule: Create valid move conditions for crossing
    @Rule(
        AS.state << State(
            left=MATCH.left,
            right=MATCH.right,
            flashlight_location="left",
            elapsed_time=MATCH.elapsed_time,
            path=MATCH.path,
            depth=MATCH.depth
        ),
        ValidTimeWindow(state_ref=MATCH.state_ref),
        SufficientPeople(state_ref=MATCH.state_ref, side="left"),
        TEST(lambda state_ref, state: state_ref == state)
    )
    def create_cross_move_condition(self, state, left, right, elapsed_time, path, depth):
        """Create valid move condition for crossing"""
        self.declare(ValidMoveCondition(
            state_ref=state,
            move_type="cross",
            left=left,
            right=right,
            elapsed_time=elapsed_time,
            path=path,
            depth=depth
        ))

    # Rule: Create valid move conditions for returning
    @Rule(
        AS.state << State(
            left=MATCH.left,
            right=MATCH.right,
            flashlight_location="right",
            elapsed_time=MATCH.elapsed_time,
            path=MATCH.path,
            depth=MATCH.depth
        ),
        ValidTimeWindow(state_ref=MATCH.state_ref),
        SufficientPeople(state_ref=MATCH.state_ref, side="right"),
        TEST(lambda state_ref, state: state_ref == state)
    )
    def create_return_move_condition(self, state, left, right, elapsed_time, path, depth):
        """Create valid move condition for returning"""
        self.declare(ValidMoveCondition(
            state_ref=state,
            move_type="return",
            left=left,
            right=right,
            elapsed_time=elapsed_time,
            path=path,
            depth=depth
        ))

    # Rule: Generate crossing moves (left to right)
    @Rule(
        ValidMoveCondition(
            state_ref=MATCH.state_ref,
            move_type="cross",
            left=MATCH.left,
            right=MATCH.right,
            elapsed_time=MATCH.elapsed_time,
            path=MATCH.path,
            depth=MATCH.depth
        )
    )
    def cross_left_to_right(self, state_ref, left, right, elapsed_time, path, depth):
        """Generate all crossing combinations"""
        left = list(left)
        right = list(right)
        for i in range(len(left)):
            for j in range(i + 1, len(left)):
                person1, person2 = left[i], left[j]
                crossing_time = max(self.people[person1], self.people[person2])

                new_left = [p for p in left if p not in [person1, person2]]
                new_right = sorted(list(right) + [person1, person2])
                new_time = elapsed_time + crossing_time
                new_path = list(path) + \
                    [("cross", (person1, person2), crossing_time)]

                # Always declare potential state - validation will be done by rules
                self.declare(PotentialState(
                    left=new_left,
                    right=new_right,
                    flashlight_location="right",
                    elapsed_time=new_time,
                    path=new_path,
                    depth=depth + 1,
                    move_type="cross"
                ))

    # Rule: Generate return moves (right to left)
    @Rule(
        ValidMoveCondition(
            state_ref=MATCH.state_ref,
            move_type="return",
            left=MATCH.left,
            right=MATCH.right,
            elapsed_time=MATCH.elapsed_time,
            path=MATCH.path,
            depth=MATCH.depth
        )
    )
    def return_right_to_left(self, state_ref, left, right, elapsed_time, path, depth):
        """Generate all return moves"""
        left = list(left)
        right = list(right)
        for person in right:
            crossing_time = self.people[person]

            new_left = sorted(list(left) + [person])
            new_right = [p for p in right if p != person]
            new_time = elapsed_time + crossing_time
            new_path = list(path) + [("return", (person,), crossing_time)]

            # Always declare potential state - validation will be done by rules
            self.declare(PotentialState(
                left=new_left,
                right=new_right,
                flashlight_location="left",
                elapsed_time=new_time,
                path=new_path,
                depth=depth + 1,
                move_type="return"
            ))

    # Rule: Record new best time for unvisited states
    @Rule(
        AS.state << State(
            left=MATCH.left,
            right=MATCH.right,
            flashlight_location=MATCH.flashlight_location,
            elapsed_time=MATCH.elapsed_time,
            path=MATCH.path
        ),
        NOT(VisitedState(
            left=MATCH.left,
            right=MATCH.right,
            flashlight_location=MATCH.flashlight_location
        ))
    )
    def record_new_state(self, state, left, right, flashlight_location, elapsed_time, path):
        """Record this as the first/best time to reach this state"""
        self.declare(VisitedState(
            left=left,
            right=right,
            flashlight_location=flashlight_location,
            best_time=elapsed_time
        ))

    # Rule: Validate potential states within time limit
    @Rule(
        AS.potential << PotentialState(
            left=MATCH.left,
            right=MATCH.right,
            flashlight_location=MATCH.flashlight_location,
            elapsed_time=MATCH.elapsed_time,
            path=MATCH.path,
            depth=MATCH.depth,
            move_type=MATCH.move_type
        ),
        TimeConstraint(max_time=MATCH.max_time),
        TEST(lambda elapsed_time, max_time: elapsed_time <= max_time)
    )
    def validate_potential_state(self, potential, left, right, flashlight_location, elapsed_time, path, depth, move_type, max_time):
        """Convert valid potential states to actual states"""
        self.declare(State(
            left=left,
            right=right,
            flashlight_location=flashlight_location,
            elapsed_time=elapsed_time,
            path=path,
            depth=depth
        ))

    # Rule: Reject potential states that exceed time limit
    @Rule(
        AS.potential << PotentialState(
            left=MATCH.left,
            right=MATCH.right,
            flashlight_location=MATCH.flashlight_location,
            elapsed_time=MATCH.elapsed_time,
            path=MATCH.path,
            depth=MATCH.depth,
            move_type=MATCH.move_type
        ),
        TimeConstraint(max_time=MATCH.max_time),
        TEST(lambda elapsed_time, max_time: elapsed_time > max_time)
    )
    def reject_potential_state(self, potential, left, right, flashlight_location, elapsed_time, path, depth, move_type, max_time):
        """Reject potential states that exceed time limit"""
        # State is automatically not converted to actual state
        pass

    # Rule: Process retraction requests
    @Rule(
        AS.retraction_request << RetractionRequest(
            state_signature=MATCH.signature,
            reason=MATCH.reason
        ),
        AS.state << State(
            left=MATCH.left,
            right=MATCH.right,
            flashlight_location=MATCH.flashlight_location,
            elapsed_time=MATCH.elapsed_time,
            path=MATCH.path,
            depth=MATCH.depth
        ),
        TEST(lambda signature, left, right, flashlight_location, elapsed_time:
             signature == (left, right, flashlight_location, elapsed_time))
    )
    def process_retraction(self, retraction_request, state, signature, reason, left, right, flashlight_location, elapsed_time, path, depth):
        """Process retraction requests declaratively"""
        self.retract(state)
        self.retract(retraction_request)

    # ===== CONSTRAINT VIOLATION RULES =====

    # Rule 1: Time Limit Violation - Mark states exceeding time limit
    @Rule(
        AS.state << State(
            left=MATCH.left,
            right=MATCH.right,
            flashlight_location=MATCH.flashlight_location,
            elapsed_time=MATCH.elapsed_time,
            path=MATCH.path,
            depth=MATCH.depth
        ),
        TimeConstraint(max_time=MATCH.max_time),
        TEST(lambda elapsed_time, max_time: elapsed_time > max_time)
    )
    def time_limit_violation(self, state, left, right, flashlight_location, elapsed_time, path, depth, max_time):
        """Mark states that exceed the time limit for retraction"""
        self.declare(StateToRetract(
            state_ref=state,
            violation_type="TIME_LIMIT_EXCEEDED",
            details=f"State time {elapsed_time} exceeds limit of {max_time} minutes"
        ))

    # Rule 2: Duplicate State Elimination - Mark worse duplicate states for retraction
    @Rule(
        AS.state1 << State(
            left=MATCH.left1,
            right=MATCH.right1,
            flashlight_location=MATCH.flashlight_location1,
            elapsed_time=MATCH.elapsed_time1,
            path=MATCH.path1,
            depth=MATCH.depth1
        ),
        AS.state2 << State(
            left=MATCH.left2,
            right=MATCH.right2,
            flashlight_location=MATCH.flashlight_location2,
            elapsed_time=MATCH.elapsed_time2,
            path=MATCH.path2,
            depth=MATCH.depth2
        ),
        TEST(lambda left1, right1, flashlight_location1, left2, right2, flashlight_location2, depth1, depth2, elapsed_time1, elapsed_time2:
             left1 == left2 and right1 == right2 and flashlight_location1 == flashlight_location2 and
             depth1 != depth2 and elapsed_time1 > elapsed_time2)
    )
    def duplicate_state_elimination(self, state1, state2, left1, right1, flashlight_location1, elapsed_time1, path1, depth1,
                                    left2, right2, flashlight_location2, elapsed_time2, path2, depth2):
        """Mark worse duplicate states for retraction"""
        self.declare(StateToRetract(
            state_ref=state1,
            violation_type="DUPLICATE_STATE",
            details=f"Duplicate state found - keeping better time {elapsed_time2} over {elapsed_time1}"
        ))

    # Rule 3: Flashlight Rule Violation - Mark states with flashlight violations
    @Rule(
        AS.state << State(
            left=MATCH.left,
            right=MATCH.right,
            flashlight_location=MATCH.flashlight_location,
            elapsed_time=MATCH.elapsed_time,
            path=MATCH.path,
            depth=MATCH.depth
        ),
        TEST(lambda left, right, flashlight_location:
             (flashlight_location == "left" and len(left) == 0) or
             (flashlight_location == "right" and len(right) == 0))
    )
    def flashlight_violation(self, state, left, right, flashlight_location, elapsed_time, path, depth):
        """Mark states where flashlight is on a side with no people"""
        self.declare(StateToRetract(
            state_ref=state,
            violation_type="FLASHLIGHT_VIOLATION",
            details=f"Flashlight on {flashlight_location} side with no people present"
        ))

    # Rule 4: Bridge Capacity Rule Violation - Mark states with too many people crossing
    @Rule(
        AS.state << State(
            left=MATCH.left,
            right=MATCH.right,
            flashlight_location=MATCH.flashlight_location,
            elapsed_time=MATCH.elapsed_time,
            path=MATCH.path,
            depth=MATCH.depth
        ),
        TEST(lambda path: len(path) > 0 and
             path[-1][0] == "cross" and len(path[-1][1]) > 2)
    )
    def bridge_capacity_violation(self, state, left, right, flashlight_location, elapsed_time, path, depth):
        """Mark states where more than 2 people attempted to cross"""
        last_move = path[-1]
        self.declare(StateToRetract(
            state_ref=state,
            violation_type="BRIDGE_CAPACITY_EXCEEDED",
            details=f"Attempted to cross {len(last_move[1])} people: {last_move[1]}"
        ))

    # Rule 5: Invalid Move Pattern Violation - Mark states with invalid move patterns
    @Rule(
        AS.state << State(
            left=MATCH.left,
            right=MATCH.right,
            flashlight_location=MATCH.flashlight_location,
            elapsed_time=MATCH.elapsed_time,
            path=MATCH.path,
            depth=MATCH.depth
        ),
        TEST(lambda path: len(path) > 0 and
             ((path[-1][0] == "cross" and len(path[-1][1]) < 2) or
              (path[-1][0] == "return" and len(path[-1][1]) != 1)))
    )
    def invalid_move_pattern(self, state, left, right, flashlight_location, elapsed_time, path, depth):
        """Mark states with invalid move patterns"""
        last_move = path[-1]
        self.declare(StateToRetract(
            state_ref=state,
            violation_type="INVALID_MOVE_PATTERN",
            details=f"Invalid move: {last_move[0]} with {len(last_move[1])} people"
        ))

    # Rule 6: Flashlight Location Consistency Violation
    @Rule(
        AS.state << State(
            left=MATCH.left,
            right=MATCH.right,
            flashlight_location=MATCH.flashlight_location,
            elapsed_time=MATCH.elapsed_time,
            path=MATCH.path,
            depth=MATCH.depth
        ),
        TEST(lambda path, flashlight_location: len(path) > 0 and
             ((path[-1][0] == "cross" and flashlight_location != "right") or
              (path[-1][0] == "return" and flashlight_location != "left")))
    )
    def flashlight_location_inconsistency(self, state, left, right, flashlight_location, elapsed_time, path, depth):
        """Mark states where flashlight location is inconsistent with last move"""
        last_move = path[-1]
        self.declare(StateToRetract(
            state_ref=state,
            violation_type="FLASHLIGHT_LOCATION_INCONSISTENT",
            details=f"Flashlight at {flashlight_location} after {last_move[0]} move"
        ))

    # Rule 7: Empty Side Crossing Violation
    @Rule(
        AS.state << State(
            left=MATCH.left,
            right=MATCH.right,
            flashlight_location=MATCH.flashlight_location,
            elapsed_time=MATCH.elapsed_time,
            path=MATCH.path,
            depth=MATCH.depth
        ),
        TEST(lambda path, left, right: len(path) > 0 and
             ((path[-1][0] == "cross" and len(left) + len(path[-1][1]) < len(left) + 2) or
              (path[-1][0] == "return" and len(right) + 1 < len(right) + 1)))
    )
    def empty_side_crossing_violation(self, state, left, right, flashlight_location, elapsed_time, path, depth):
        """Mark states where people cross from wrong side"""
        last_move = path[-1]
        self.declare(StateToRetract(
            state_ref=state,
            violation_type="EMPTY_SIDE_CROSSING",
            details=f"Invalid {last_move[0]} from empty side"
        ))

    # Rule 8: Execute retraction of marked states
    @Rule(
        AS.retraction_marker << StateToRetract(
            state_ref=MATCH.state_ref,
            violation_type=MATCH.violation_type,
            details=MATCH.details
        )
    )
    def execute_state_retraction(self, retraction_marker, state_ref, violation_type, details):
        """Execute retraction of states marked for removal"""
        self.retract(state_ref)
        self.retract(retraction_marker)
        print(f"CONSTRAINT VIOLATION [{violation_type}]: {details}")

    # Rule: Prune worse paths using state reference
    @Rule(
        AS.state << State(
            left=MATCH.left,
            right=MATCH.right,
            flashlight_location=MATCH.flashlight_location,
            elapsed_time=MATCH.elapsed_time,
            path=MATCH.path,
            depth=MATCH.depth
        ),
        VisitedState(
            left=MATCH.left,
            right=MATCH.right,
            flashlight_location=MATCH.flashlight_location,
            best_time=MATCH.best_time
        ),
        TEST(lambda elapsed_time, best_time: elapsed_time > best_time)
    )
    def prune_worse_path(self, state, left, right, flashlight_location, elapsed_time, path, depth, best_time):
        """Remove states that are worse than previously visited"""
        self.retract(state)

    # Rule: Update best time for better paths
    @Rule(
        AS.state << State(
            left=MATCH.left,
            right=MATCH.right,
            flashlight_location=MATCH.flashlight_location,
            elapsed_time=MATCH.elapsed_time,
            path=MATCH.path,
            depth=MATCH.depth
        ),
        AS.visited << VisitedState(
            left=MATCH.left,
            right=MATCH.right,
            flashlight_location=MATCH.flashlight_location,
            best_time=MATCH.best_time
        ),
        TEST(lambda elapsed_time, best_time: elapsed_time < best_time)
    )
    def update_best_time(self, state, visited, left, right, flashlight_location, elapsed_time, path, depth, best_time):
        """Update best time for states with better paths"""
        self.retract(visited)
        self.declare(VisitedState(
            left=left,
            right=right,
            flashlight_location=flashlight_location,
            best_time=elapsed_time
        ))

    # Rule: Goal detection - all people on right side (MODIFIED TO ALLOW MULTIPLE SOLUTIONS)
    @Rule(
        AS.state << State(
            left=MATCH.left,
            right=MATCH.right,
            flashlight_location="right",
            elapsed_time=MATCH.elapsed_time,
            path=MATCH.path
        ),
        TimeConstraint(max_time=MATCH.max_time),
        TEST(lambda left: len(left) == 0),
        TEST(lambda right: len(right) == 4),
        TEST(lambda elapsed_time, max_time: elapsed_time <= max_time)
    )
    def goal_reached(self, state, right, elapsed_time, path, max_time):
        """Solution found - all people crossed successfully"""
        self.solution_count += 1
        # Store solution in instance variable
        self.solutions.append({
            'moves': list(path),
            'total_time': elapsed_time,
            'solution_number': self.solution_count
        })

        # Create a unique Solution fact for each solution
        self.declare(Solution(
            moves=path,
            total_time=elapsed_time,
            solution_id=self.solution_count
        ))

    # Rule: Print solution when found (MODIFIED TO HANDLE MULTIPLE SOLUTIONS)
    @Rule(
        AS.solution << Solution(
            moves=MATCH.moves,
            total_time=MATCH.total_time,
            solution_id=MATCH.solution_id
        ),
        # Only print each solution once
        NOT(SolutionPrinted(solution_id=MATCH.solution_id))
    )
    def print_solution(self, solution, moves, total_time, solution_id):
        """Print each solution as it's found"""
        print(f"\n{'='*60}")
        print(
            f"SOLUTION {solution_id} FOUND (Total time: {total_time} minutes):")
        print('='*60)

        # Print moves in correct order (reverse chronological)
        for i, move in enumerate(reversed(moves), 1):
            action, people, time_taken = move
            if action == "cross":
                if len(people) == 2:
                    print(
                        f"Step {i}: {people[0]} and {people[1]} cross together → {time_taken} minutes")
                else:
                    print(
                        f"Step {i}: {', '.join(people)} cross together → {time_taken} minutes")
            elif action == "return":
                print(
                    f"Step {i}: {people[0]} returns with flashlight → {time_taken} minutes")

        print("-" * 60)
        print(f"SUCCESS: All 4 people crossed in {total_time} minutes!")
        print(f"Zombies arrive in 17.0 minutes - SAFE! ✓")
        print('='*60)

        # Mark this solution as printed
        self.declare(SolutionPrinted(solution_id=solution_id))

    # Rule: Log each new state as a node in the search tree
    @Rule(
        AS.state << State(
            left=MATCH.left,
            right=MATCH.right,
            flashlight_location=MATCH.flashlight_location,
            elapsed_time=MATCH.elapsed_time,
            path=MATCH.path,
            depth=MATCH.depth
        ),
        TEST(lambda depth: depth > 0)  # Skip initial state
    )
    def log_search_tree_node(self, state, left, right, flashlight_location, elapsed_time, path, depth):
        """Log each node in the search tree with indentation and clear formatting"""
        last_action = path[-1] if path else (None, (), 0)
        action, people, time_taken = last_action
        # Convert frozenlists to plain lists for display
        left_list = list(left)
        right_list = list(right)
        people_str = ", ".join(people)
        # Indentation and tree structure
        indent = "    " * (depth - 1)
        branch = "└─" if depth > 1 else ""
        print(f"{indent}{branch}[Depth {depth}] {action}: {people_str}")
        print(f"{indent}    Left: {left_list} | Right: {right_list} | Flashlight: {flashlight_location} | Time: {elapsed_time}")

    def print_final_summary(self):
        """Print summary of all solutions found"""
        print(f"\n{'='*80}")
        print(f"FINAL SUMMARY: {len(self.solutions)} SOLUTION(S) FOUND")
        print('='*80)

        if self.solutions:
            for i, sol in enumerate(self.solutions, 1):
                print(f"\nSolution {i}: {sol['total_time']} minutes")
                for j, move in enumerate(reversed(sol['moves']), 1):
                    action, people, time_taken = move
                    if action == "cross":
                        print(
                            f"  Step {j}: {people[0]} and {people[1]} cross → {time_taken} min")
                    else:
                        print(
                            f"  Step {j}: {people[0]} returns → {time_taken} min")
        else:
            print("No solutions found within the time limit.")

        print('='*80)
