from facts import *
from experta import *
import collections
import collections.abc

collections.Mapping = collections.abc.Mapping


class BridgePuzzleSolverConstraints(KnowledgeEngine):
    @Rule(
        AS.retraction_request
        << RetractionRequest(state_signature=MATCH.signature, reason=MATCH.reason),
        AS.state
        << State(
            left=MATCH.left,
            right=MATCH.right,
            flashlight_location=MATCH.flashlight_location,
            elapsed_time=MATCH.elapsed_time,
            path=MATCH.path,
            depth=MATCH.depth,
        ),
        TEST(
            lambda signature, left, right, flashlight_location, elapsed_time: signature
            == (left, right, flashlight_location, elapsed_time)
        ),
    )
    def process_retraction(self, retraction_request, state):
        self.retract(state)
        self.retract(retraction_request)

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
        TimeConstraint(max_time=MATCH.max_time),
        TEST(lambda elapsed_time, max_time: elapsed_time > max_time),
    )
    def time_limit_violation(self, state, elapsed_time, max_time):
        self.declare(
            StateToRetract(
                state_ref=state,
                violation_type="TIME_LIMIT_EXCEEDED",
                details=f"State time {elapsed_time} exceeds limit of {max_time} minutes",
            )
        )

    @Rule(
        AS.state1
        << State(
            left=MATCH.left1,
            right=MATCH.right1,
            flashlight_location=MATCH.flashlight_location1,
            elapsed_time=MATCH.elapsed_time1,
            path=MATCH.path1,
            depth=MATCH.depth1,
        ),
        AS.state2
        << State(
            left=MATCH.left2,
            right=MATCH.right2,
            flashlight_location=MATCH.flashlight_location2,
            elapsed_time=MATCH.elapsed_time2,
            path=MATCH.path2,
            depth=MATCH.depth2,
        ),
        TEST(
            lambda left1, right1, flashlight_location1, left2, right2, flashlight_location2, depth1, depth2, elapsed_time1, elapsed_time2: left1
            == left2
            and right1 == right2
            and flashlight_location1 == flashlight_location2
            and depth1 != depth2
            and elapsed_time1 > elapsed_time2
        ),
    )
    def duplicate_state_elimination(self, state1, elapsed_time1, elapsed_time2):
        self.declare(
            StateToRetract(
                state_ref=state1,
                violation_type="DUPLICATE_STATE",
                details=f"Duplicate state found - keeping better time {elapsed_time2} over {elapsed_time1}",
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
        TEST(
            lambda left, right, flashlight_location: (
                flashlight_location == "left" and len(left) == 0
            )
            or (flashlight_location == "right" and len(right) == 0)
        ),
    )
    def flashlight_violation(self, state, flashlight_location):
        self.declare(
            StateToRetract(
                state_ref=state,
                violation_type="FLASHLIGHT_VIOLATION",
                details=f"Flashlight on {flashlight_location} side with no people present",
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
        TEST(
            lambda path: len(path) > 0
            and path[-1][0] == "cross"
            and len(path[-1][1]) > 2
        ),
    )
    def bridge_capacity_violation(self, state, path):
        last_move = path[-1]
        self.declare(
            StateToRetract(
                state_ref=state,
                violation_type="BRIDGE_CAPACITY_EXCEEDED",
                details=f"Attempted to cross {len(last_move[1])} people: {last_move[1]}",
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
        TEST(
            lambda path: len(path) > 0
            and (
                (path[-1][0] == "cross" and len(path[-1][1]) < 2)
                or (path[-1][0] == "return" and len(path[-1][1]) != 1)
            )
        ),
    )
    def invalid_move_pattern(self, state, path):
        last_move = path[-1]
        self.declare(
            StateToRetract(
                state_ref=state,
                violation_type="INVALID_MOVE_PATTERN",
                details=f"Invalid move: {last_move[0]} with {len(last_move[1])} people",
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
        TEST(
            lambda path, flashlight_location: len(path) > 0
            and (
                (path[-1][0] == "cross" and flashlight_location != "right")
                or (path[-1][0] == "return" and flashlight_location != "left")
            )
        ),
    )
    def flashlight_location_inconsistency(self, state, flashlight_location, path):
        last_move = path[-1]
        self.declare(
            StateToRetract(
                state_ref=state,
                violation_type="FLASHLIGHT_LOCATION_INCONSISTENT",
                details=f"Flashlight at {flashlight_location} after {last_move[0]} move",
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
        TEST(
            lambda path, left, right: len(path) > 0
            and (
                (
                    path[-1][0] == "cross"
                    and len(left) + len(path[-1][1]) < len(left) + 2
                )
                or (path[-1][0] == "return" and len(right) + 1 < len(right) + 1)
            )
        ),
    )
    def empty_side_crossing_violation(self, state, path):
        last_move = path[-1]
        self.declare(
            StateToRetract(
                state_ref=state,
                violation_type="EMPTY_SIDE_CROSSING",
                details=f"Invalid {last_move[0]} from empty side",
            )
        )

    @Rule(
        AS.retraction_marker
        << StateToRetract(
            state_ref=MATCH.state_ref,
            violation_type=MATCH.violation_type,
            details=MATCH.details,
        )
    )
    def execute_state_retraction(
        self, retraction_marker, state_ref, violation_type, details
    ):
        self.retract(state_ref)
        self.retract(retraction_marker)
        print(f"CONSTRAINT VIOLATION [{violation_type}]: {details}")

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
        VisitedState(
            left=MATCH.left,
            right=MATCH.right,
            flashlight_location=MATCH.flashlight_location,
            best_time=MATCH.best_time,
        ),
        TEST(lambda elapsed_time, best_time: elapsed_time > best_time),
    )
    def prune_worse_path(self, state):
        self.retract(state)

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
        AS.visited
        << VisitedState(
            left=MATCH.left,
            right=MATCH.right,
            flashlight_location=MATCH.flashlight_location,
            best_time=MATCH.best_time,
        ),
        TEST(lambda elapsed_time, best_time: elapsed_time < best_time),
    )
    def update_best_time(self, visited, left, right, flashlight_location, elapsed_time):
        self.retract(visited)
        self.declare(
            VisitedState(
                left=left,
                right=right,
                flashlight_location=flashlight_location,
                best_time=elapsed_time,
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
        ),
        TimeConstraint(max_time=MATCH.max_time),
        TEST(lambda left: len(left) == 0),
        TEST(lambda right: len(right) == 4),
        TEST(lambda elapsed_time, max_time: elapsed_time <= max_time),
    )
    def goal_reached(self, elapsed_time, path):
        self.solution_count += 1
        self.solutions.append(
            {
                "moves": list(path),
                "total_time": elapsed_time,
                "solution_number": self.solution_count,
            }
        )
        self.declare(
            Solution(
                moves=path, total_time=elapsed_time, solution_id=self.solution_count
            )
        )

    @Rule(
        AS.solution
        << Solution(
            moves=MATCH.moves,
            total_time=MATCH.total_time,
            solution_id=MATCH.solution_id,
        ),
        NOT(SolutionPrinted(solution_id=MATCH.solution_id)),
    )
    def print_solution(self, moves, total_time, solution_id):
        print(f"{'='*60}")
        print(
            f"\033[1mSOLUTION {solution_id} FOUND (Total time: {total_time} minutes):\033[0m"
        )
        print("=" * 60)
        for i, move in enumerate(reversed(moves), 1):
            action, people, time_taken = move

            action_handlers = {
                "cross": lambda: self.handle_cross_action(i, people, time_taken),
                "return": lambda: self.handle_return_action(i, people, time_taken),
            }
            action_handlers.get(action, lambda: None)()

        print("-" * 60)
        print(f"\033[32mSUCCESS: All 4 people crossed in {total_time} minutes!\033[0m")
        print("=" * 60)
        print("")
        self.declare(SolutionPrinted(solution_id=solution_id))

    def handle_cross_action(self, step, people, time_taken):
        people_count = len(people)
        cross_handlers = {
            2: lambda: print(
                f"\033[31mStep {step}:\033[0m {people[0]} and {people[1]} cross together ⨠ \033[34m{time_taken} minutes\033[0m"
            ),
            1: lambda: print(
                f"\033[31mStep {step}:\033[0m {people[0]} crosses alone ⨠ \033[34m{time_taken} minutes\033[0m"
            ),
        }

        def default_handler():
            return print(
                f"\033[31mStep {step}:\033[0m {', '.join(people)} cross together ⨠ \033[34m{time_taken} minutes\033[0m"
            )

        cross_handlers.get(people_count, default_handler)()

    def handle_return_action(self, step, people, time_taken):
        print(
            f"\033[31mStep {step}:\033[0m {people[0]} returns with flashlight ⨠ \033[34m{time_taken} minutes\033[0m"
        )
