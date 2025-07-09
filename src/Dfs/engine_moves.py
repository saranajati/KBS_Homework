from facts import *
from experta import *
import collections
import collections.abc

collections.Mapping = collections.abc.Mapping


class BridgePuzzleSolverMoves(KnowledgeEngine):
    def __init__(self, people, max_time=17):
        super().__init__()
        self.people = {name: float(time) for name, time in people}
        self.max_time = float(max_time)
        self.solutions = []
        self.solution_count = 0

    @Rule()
    def initialize(self):
        left_side = list(self.people.keys())
        self.declare(
            State(
                left=left_side,
                right=[],
                flashlight_location="left",
                elapsed_time=0.0,
                path=[],
                depth=0,
            )
        )
        self.declare(TimeConstraint(max_time=17.0))

    @Rule(
        AS.state << State(elapsed_time=MATCH.elapsed_time),
        TimeConstraint(max_time=MATCH.max_time),
        TEST(lambda elapsed_time, max_time: elapsed_time < max_time),
    )
    def mark_valid_time_window(self, state, elapsed_time):
        self.declare(ValidTimeWindow(state_ref=state, elapsed_time=elapsed_time))

    @Rule(
        AS.state << State(left=MATCH.left, flashlight_location="left"),
        TEST(lambda left: len(left) >= 2),
    )
    def mark_sufficient_people_left(self, state, left):
        self.declare(SufficientPeople(state_ref=state, side="left", count=len(left)))

    @Rule(
        AS.state
        << State(left=MATCH.left, right=MATCH.right, flashlight_location="right"),
        TEST(lambda right: len(right) >= 1),
        TEST(lambda left: len(left) > 0),
    )
    def mark_sufficient_people_right(self, state, right):
        self.declare(SufficientPeople(state_ref=state, side="right", count=len(right)))

    @Rule(
        AS.state
        << State(
            left=MATCH.left,
            right=MATCH.right,
            flashlight_location="left",
            elapsed_time=MATCH.elapsed_time,
            path=MATCH.path,
            depth=MATCH.depth,
        ),
        ValidTimeWindow(state_ref=MATCH.state_ref),
        SufficientPeople(state_ref=MATCH.state_ref, side="left"),
        TEST(lambda state_ref, state: state_ref == state),
    )
    def create_cross_move_condition(
        self, state, left, right, elapsed_time, path, depth
    ):
        self.declare(
            ValidMoveCondition(
                state_ref=state,
                move_type="cross",
                left=left,
                right=right,
                elapsed_time=elapsed_time,
                path=path,
                depth=depth,
            )
        )

    @Rule(
        AS.state
        << State(
            left=MATCH.left,
            right=MATCH.right,
            flashlight_location="right",
            elapsed_time=MATCH.elapsed_time,
            path=MATCH.path,
            depth=MATCH.depth,
        ),
        ValidTimeWindow(state_ref=MATCH.state_ref),
        SufficientPeople(state_ref=MATCH.state_ref, side="right"),
        TEST(lambda state_ref, state: state_ref == state),
    )
    def create_return_move_condition(
        self, state, left, right, elapsed_time, path, depth
    ):
        self.declare(
            ValidMoveCondition(
                state_ref=state,
                move_type="return",
                left=left,
                right=right,
                elapsed_time=elapsed_time,
                path=path,
                depth=depth,
            )
        )

    @Rule(
        ValidMoveCondition(
            state_ref=MATCH.state_ref,
            move_type="cross",
            left=MATCH.left,
            right=MATCH.right,
            elapsed_time=MATCH.elapsed_time,
            path=MATCH.path,
            depth=MATCH.depth,
        )
    )
    def cross_left_to_right(self, left, right, elapsed_time, path, depth):
        left = list(left)
        right = list(right)
        for i in range(len(left)):
            for j in range(i + 1, len(left)):
                person1, person2 = left[i], left[j]
                crossing_time = max(self.people[person1], self.people[person2])

                excluded_people = {person1, person2}
                new_left = list(filter(lambda p: p not in excluded_people, left))
                new_right = sorted(list(right) + [person1, person2])
                new_time = elapsed_time + crossing_time
                new_path = list(path) + [("cross", (person1, person2), crossing_time)]

                self.declare(
                    PotentialState(
                        left=new_left,
                        right=new_right,
                        flashlight_location="right",
                        elapsed_time=new_time,
                        path=new_path,
                        depth=depth + 1,
                        move_type="cross",
                    )
                )

    @Rule(
        ValidMoveCondition(
            state_ref=MATCH.state_ref,
            move_type="return",
            left=MATCH.left,
            right=MATCH.right,
            elapsed_time=MATCH.elapsed_time,
            path=MATCH.path,
            depth=MATCH.depth,
        )
    )
    def return_right_to_left(self, left, right, elapsed_time, path, depth):
        left = list(left)
        right = list(right)
        for person in right:
            crossing_time = self.people[person]

            new_left = sorted(list(left) + [person])
            new_right = list(filter(lambda p: p != person, right))
            new_time = elapsed_time + crossing_time
            new_path = list(path) + [("return", (person,), crossing_time)]

            self.declare(
                PotentialState(
                    left=new_left,
                    right=new_right,
                    flashlight_location="left",
                    elapsed_time=new_time,
                    path=new_path,
                    depth=depth + 1,
                    move_type="return",
                )
            )

    @Rule(
        AS.state
        << State(
            left=MATCH.left,
            right=MATCH.right,
            flashlight_location=MATCH.flashlight_location,
            elapsed_time=MATCH.elapsed_time,
            path=MATCH.path,
        ),
        NOT(
            VisitedState(
                left=MATCH.left,
                right=MATCH.right,
                flashlight_location=MATCH.flashlight_location,
            )
        ),
    )
    def record_new_state(self, left, right, flashlight_location, elapsed_time):
        self.declare(
            VisitedState(
                left=left,
                right=right,
                flashlight_location=flashlight_location,
                best_time=elapsed_time,
            )
        )

    @Rule(
        AS.potential
        << PotentialState(
            left=MATCH.left,
            right=MATCH.right,
            flashlight_location=MATCH.flashlight_location,
            elapsed_time=MATCH.elapsed_time,
            path=MATCH.path,
            depth=MATCH.depth,
            move_type=MATCH.move_type,
        ),
        TimeConstraint(max_time=MATCH.max_time),
        TEST(lambda elapsed_time, max_time: elapsed_time <= max_time),
    )
    def validate_potential_state(
        self, left, right, flashlight_location, elapsed_time, path, depth
    ):
        self.declare(
            State(
                left=left,
                right=right,
                flashlight_location=flashlight_location,
                elapsed_time=elapsed_time,
                path=path,
                depth=depth,
            )
        )

    @Rule(
        AS.state
        << State(
            left=MATCH.left,
            right=MATCH.right,
            flashlight_location=MATCH.flashlight_location,
            elapsed_time=MATCH.elapsed_time,
            path=MATCH.path,
            depth=MATCH.depth,
        ),
        TEST(lambda depth: depth > 0),
    )
    def log_search_tree_node(
        self, left, right, flashlight_location, elapsed_time, path, depth
    ):
        last_action = path[-1] or (None, (), 0)
        action, people, time_taken = last_action
        left_list = list(left)
        right_list = list(right)
        people_str = ", ".join(people)
        print(f"⟬Branch {depth}⟭ {action}: {people_str}")
        print(f"\033[31m⬅️  Left: {left_list}\033[0m")
        print(f"\033[34m➡️  Right: {right_list}\033[0m")
        print(
            f"\033[33m🔦  Flashlight: {flashlight_location}\033[0m   \033[32m⏱️  Time: {elapsed_time}\033[0m"
        )
        print("")

        # action_handlers = {
        #     "cross": lambda: print(
        #         f"Action: {people[0]} and {people[1]} cross together → {time_taken} min"
        #     ),
        #     "return": lambda: print(
        #         f"Action: {people[0]} returns with flashlight → {time_taken} min"
        #     ),
        # }
        # action_handlers.get(action, lambda: None)()
