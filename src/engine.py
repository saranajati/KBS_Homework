from facts import *
from experta import *
import collections
import collections.abc
collections.Mapping = collections.abc.Mapping

# Define additional facts for declarative processing


class PotentialState(Fact):
    """Represents a potential state before validation"""
    pass


class RetractionRequest(Fact):
    """Represents a request to retract a state"""
    pass


class ConstraintViolation(Fact):
    """Represents a constraint violation that requires state retraction"""
    pass


class BridgePuzzleSolver(KnowledgeEngine):
    def __init__(self, people, max_time=17):
        super().__init__()
        # Convert all times to float to match fact field types
        self.people = {name: float(time) for name, time in people}
        self.max_time = float(max_time)
        self.solution_found = False

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

    # Rule: Generate crossing moves (left to right)
    @Rule(
        State(
            left=MATCH.left,
            right=MATCH.right,
            flashlight_location="left",
            elapsed_time=MATCH.elapsed_time,
            path=MATCH.path,
            depth=MATCH.depth
        ),
        TEST(lambda left: len(left) >= 2),
        TEST(lambda elapsed_time: elapsed_time < 17),
        NOT(Solution())  # Don't generate moves after solution found
    )
    def cross_left_to_right(self, left, right, elapsed_time, path, depth):
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
        State(
            left=MATCH.left,
            right=MATCH.right,
            flashlight_location="right",
            elapsed_time=MATCH.elapsed_time,
            path=MATCH.path,
            depth=MATCH.depth
        ),
        TEST(lambda right: len(right) >= 1),
        TEST(lambda left: len(left) > 0),  # Don't return if everyone is across
        TEST(lambda elapsed_time: elapsed_time < 17),
        NOT(Solution())  # Don't generate moves after solution found
    )
    def return_right_to_left(self, left, right, elapsed_time, path, depth):
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
        State(
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
    def record_new_state(self, left, right, flashlight_location, elapsed_time, path):
        """Record this as the first/best time to reach this state"""
        self.declare(VisitedState(
            left=left,
            right=right,
            flashlight_location=flashlight_location,
            best_time=elapsed_time
        ))

    # Rule: Validate potential states within time limit
    @Rule(
        PotentialState(
            left=MATCH.left,
            right=MATCH.right,
            flashlight_location=MATCH.flashlight_location,
            elapsed_time=MATCH.elapsed_time,
            path=MATCH.path,
            depth=MATCH.depth,
            move_type=MATCH.move_type
        ),
        TEST(lambda elapsed_time: elapsed_time <= 17)
    )
    def validate_potential_state(self, left, right, flashlight_location, elapsed_time, path, depth, move_type):
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
        PotentialState(
            left=MATCH.left,
            right=MATCH.right,
            flashlight_location=MATCH.flashlight_location,
            elapsed_time=MATCH.elapsed_time,
            path=MATCH.path,
            depth=MATCH.depth,
            move_type=MATCH.move_type
        ),
        TEST(lambda elapsed_time: elapsed_time > 17)
    )
    def reject_potential_state(self, left, right, flashlight_location, elapsed_time, path, depth, move_type):
        """Reject potential states that exceed time limit"""
        # State is automatically not converted to actual state
        pass

    # Rule: Process retraction requests
    @Rule(
        RetractionRequest(
            state_signature=MATCH.signature,
            reason=MATCH.reason
        ),
        State(
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
    def process_retraction(self, signature, reason, left, right, flashlight_location, elapsed_time, path, depth):
        """Process retraction requests declaratively"""
        # Find and retract the matching state
        for fact in self.facts:
            if (isinstance(fact, State) and
                fact['left'] == left and
                fact['right'] == right and
                fact['flashlight_location'] == flashlight_location and
                    fact['elapsed_time'] == elapsed_time):
                self.retract(fact)
                break

    # ===== CONSTRAINT VIOLATION RULES =====

    # Rule 1: Time Limit Violation - Discard states exceeding 17 minutes
    @Rule(
        State(
            left=MATCH.left,
            right=MATCH.right,
            flashlight_location=MATCH.flashlight_location,
            elapsed_time=MATCH.elapsed_time,
            path=MATCH.path,
            depth=MATCH.depth
        ),
        TEST(lambda elapsed_time: elapsed_time > 17)
    )
    def time_limit_violation(self, left, right, flashlight_location, elapsed_time, path, depth):
        """Discard states that exceed the 17-minute time limit"""
        self.declare(ConstraintViolation(
            violation_type="TIME_LIMIT_EXCEEDED",
            state_signature=(left, right, flashlight_location, elapsed_time),
            details=f"State time {elapsed_time} exceeds limit of 17 minutes"
        ))

    # Rule 2: Duplicate State Elimination - Prevent loops and cycles
    @Rule(
        State(
            left=MATCH.left1,
            right=MATCH.right1,
            flashlight_location=MATCH.flashlight_location1,
            elapsed_time=MATCH.elapsed_time1,
            path=MATCH.path1,
            depth=MATCH.depth1
        ),
        State(
            left=MATCH.left2,
            right=MATCH.right2,
            flashlight_location=MATCH.flashlight_location2,
            elapsed_time=MATCH.elapsed_time2,
            path=MATCH.path2,
            depth=MATCH.depth2
        ),
        TEST(lambda left1, right1, flashlight_location1, left2, right2, flashlight_location2, depth1, depth2:
             left1 == left2 and right1 == right2 and flashlight_location1 == flashlight_location2 and depth1 != depth2)
    )
    def duplicate_state_elimination(self, left1, right1, flashlight_location1, elapsed_time1, path1, depth1,
                                    left2, right2, flashlight_location2, elapsed_time2, path2, depth2):
        """Discard duplicate states that appear at different depths"""
        # Keep the state with shorter elapsed time, discard the worse one
        worse_time = max(elapsed_time1, elapsed_time2)
        self.declare(ConstraintViolation(
            violation_type="DUPLICATE_STATE",
            state_signature=(left1, right1, flashlight_location1, worse_time),
            details=f"Duplicate state found at different depths: {depth1} vs {depth2}"
        ))

    # Rule 3: Flashlight Rule Violation - Ensure flashlight is always present during crossings
    @Rule(
        State(
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
    def flashlight_violation(self, left, right, flashlight_location, elapsed_time, path, depth):
        """Discard states where flashlight is on a side with no people"""
        self.declare(ConstraintViolation(
            violation_type="FLASHLIGHT_VIOLATION",
            state_signature=(left, right, flashlight_location, elapsed_time),
            details=f"Flashlight on {flashlight_location} side with no people present"
        ))

    # Rule 4: Bridge Capacity Rule Violation - Prevent more than 2 people crossing
    @Rule(
        State(
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
    def bridge_capacity_violation(self, left, right, flashlight_location, elapsed_time, path, depth):
        """Discard states where more than 2 people attempted to cross"""
        last_move = path[-1]
        self.declare(ConstraintViolation(
            violation_type="BRIDGE_CAPACITY_EXCEEDED",
            state_signature=(left, right, flashlight_location, elapsed_time),
            details=f"Attempted to cross {len(last_move[1])} people: {last_move[1]}"
        ))

    # Rule 5: Invalid Move Pattern Violation - Ensure proper crossing patterns
    @Rule(
        State(
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
    def invalid_move_pattern(self, left, right, flashlight_location, elapsed_time, path, depth):
        """Discard states with invalid move patterns"""
        last_move = path[-1]
        self.declare(ConstraintViolation(
            violation_type="INVALID_MOVE_PATTERN",
            state_signature=(left, right, flashlight_location, elapsed_time),
            details=f"Invalid move: {last_move[0]} with {len(last_move[1])} people"
        ))

    # Rule 6: Flashlight Location Consistency Violation
    @Rule(
        State(
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
    def flashlight_location_inconsistency(self, left, right, flashlight_location, elapsed_time, path, depth):
        """Discard states where flashlight location is inconsistent with last move"""
        last_move = path[-1]
        self.declare(ConstraintViolation(
            violation_type="FLASHLIGHT_LOCATION_INCONSISTENT",
            state_signature=(left, right, flashlight_location, elapsed_time),
            details=f"Flashlight at {flashlight_location} after {last_move[0]} move"
        ))

    # Rule 7: Empty Side Crossing Violation
    @Rule(
        State(
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
    def empty_side_crossing_violation(self, left, right, flashlight_location, elapsed_time, path, depth):
        """Discard states where people cross from wrong side"""
        last_move = path[-1]
        self.declare(ConstraintViolation(
            violation_type="EMPTY_SIDE_CROSSING",
            state_signature=(left, right, flashlight_location, elapsed_time),
            details=f"Invalid {last_move[0]} from empty side"
        ))

    # Rule 8: Process all constraint violations by retracting violating states
    @Rule(
        ConstraintViolation(
            violation_type=MATCH.violation_type,
            state_signature=MATCH.signature,
            details=MATCH.details
        ),
        State(
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
    def process_constraint_violation(self, violation_type, signature, details, left, right, flashlight_location, elapsed_time, path, depth):
        """Process constraint violations by retracting violating states"""
        # Find and retract the violating state
        for fact in self.facts:
            if (isinstance(fact, State) and
                fact['left'] == left and
                fact['right'] == right and
                fact['flashlight_location'] == flashlight_location and
                    fact['elapsed_time'] == elapsed_time):
                self.retract(fact)
                # Optional: Log the violation for debugging
                print(f"CONSTRAINT VIOLATION [{violation_type}]: {details}")
                break

    @Rule(
        State(
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
        TEST(lambda elapsed_time, best_time: elapsed_time >= best_time)
    )
    def prune_worse_path(self, left, right, flashlight_location, elapsed_time, path, depth):
        """Remove states that are worse than previously visited"""
        # Find and retract the worse state
        for fact in self.facts:
            if (isinstance(fact, State) and
                fact['left'] == left and
                fact['right'] == right and
                fact['flashlight_location'] == flashlight_location and
                    fact['elapsed_time'] == elapsed_time):
                self.retract(fact)
                break

    # Rule: Goal detection - all people on right side
    @Rule(
        State(
            left=MATCH.left,
            right=MATCH.right,
            flashlight_location="right",
            elapsed_time=MATCH.elapsed_time,
            path=MATCH.path
        ),
        TEST(lambda left: len(left) == 0),
        TEST(lambda right: len(right) == 4),
        TEST(lambda elapsed_time: elapsed_time <= 17),
        NOT(Solution())  # Only fire once
    )
    def goal_reached(self, right, elapsed_time, path):
        """Solution found - all people crossed successfully"""
        self.solution_found = True

        # Store solution for printing
        self.declare(Solution(moves=path, total_time=elapsed_time))

    # Rule: Print solution header when solution is found
    @Rule(
        Solution(
            moves=MATCH.moves,
            total_time=MATCH.total_time
        ),
        NOT(PrintMove())  # Only print header before any moves are printed
    )
    def print_solution_header(self, moves, total_time):
        """Print solution header and create PrintMove facts"""
        print(f"\nSOLUTION FOUND (Total time: {total_time} minutes):")
        print("-" * 50)

        # Create PrintMove facts for each step
        for i, move in enumerate(moves, 1):
            action, people, time_taken = move
            self.declare(PrintMove(
                step=i,
                action=action,
                people=people,
                time=float(time_taken)
            ))

    # Rule: Print crossing moves (2 people)
    @Rule(
        PrintMove(
            step=MATCH.step,
            action="cross",
            people=MATCH.people,
            time=MATCH.time
        ),
        TEST(lambda people: len(people) == 2)
    )
    def print_cross_move(self, step, people, time):
        """Print crossing move"""
        print(
            f"Step {step}: {people[0]} and {people[1]} cross together → {time} minutes")

    # Rule: Print return moves (1 person)
    @Rule(
        PrintMove(
            step=MATCH.step,
            action="return",
            people=MATCH.people,
            time=MATCH.time
        ),
        TEST(lambda people: len(people) == 1)
    )
    def print_return_move(self, step, people, time):
        """Print return move"""
        print(
            f"Step {step}: {people[0]} returns with flashlight → {time} minutes")

    # Rule: Print solution summary after all moves
    @Rule(
        Solution(
            moves=MATCH.moves,
            total_time=MATCH.total_time
        ),
        TEST(lambda total_time: total_time <= 17)
    )
    def print_solution_summary(self, moves, total_time):
        """Print final solution summary"""
        print("-" * 50)
        print(f"SUCCESS: All 4 people crossed in {total_time} minutes!")
        print(f"Zombies arrive in 17 minutes - SAFE! ✓")


# Example usage:
def solve_bridge_puzzle():
    # Define people and their crossing times
    people = {
        "You": 1,
        "Lab Assistant": 2,
        "Worker": 5,
        "Scientist": 10
    }

    # Create and run solver
    solver = BridgePuzzleSolver(people, max_time=17)
    solver.reset()
    solver.run()

    # Check solution status without if statement
    solution_status = solver.solution_found
    print(f"Solution found: {solution_status}")

    return solver.solution_found


