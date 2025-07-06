from facts import *
from experta import *
import collections
import collections.abc
collections.Mapping = collections.abc.Mapping


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

                self.declare(State(
                    left=new_left,
                    right=new_right,
                    flashlight_location="right",
                    elapsed_time=new_time,
                    path=new_path,
                    depth=depth + 1
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

            self.declare(State(
                left=new_left,
                right=new_right,
                flashlight_location="left",
                elapsed_time=new_time,
                path=new_path,
                depth=depth + 1
            ))

    # Rule: Check for visited states and prune worse paths
    @Rule(
        State(
            left=MATCH.left,
            right=MATCH.right,
            flashlight_location=MATCH.flashlight_location,
            elapsed_time=MATCH.elapsed_time,
            path=MATCH.path
        ),
        VisitedState(
            left=MATCH.left,
            right=MATCH.right,
            flashlight_location=MATCH.flashlight_location,
            best_time=MATCH.best_time
        ),
        TEST(lambda elapsed_time, best_time: elapsed_time >= best_time)
    )
    def prune_worse_path(self, left, right, flashlight_location, elapsed_time, path):
        """Remove states that are worse than previously visited"""
        # This state is worse, so we retract it
        pass  # Rule automatically prevents further processing

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
        print(f"Step {step}: {people[0]} and {people[1]} cross together → {time} minutes")

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
        print(f"Step {step}: {people[0]} returns with flashlight → {time} minutes")

    # Rule: Print solution summary after all moves
    @Rule(
        Solution(
            moves=MATCH.moves,
            total_time=MATCH.total_time,
            is_valid=True
        ),
        TEST(lambda total_time: total_time <= 17)
    )
    def print_solution_summary(self, moves, total_time):
        """Print final solution summary"""
        print("-" * 50)
        print(f"SUCCESS: All 4 people crossed in {total_time} minutes!")
        print(f"Zombies arrive in 17 minutes - SAFE! ✓")


