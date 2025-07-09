from facts import *
from experta import *
import collections
import collections.abc
collections.Mapping = collections.abc.Mapping


class BridgePuzzleSolverConstraintsBfs(KnowledgeEngine):
    def __init__(self):
        super().__init__()
        self.solution_signatures = set()

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
            sequence=MATCH.sequence,
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
            sequence=MATCH.sequence,
        ),
        TimeConstraint(max_time=MATCH.max_time),
        TEST(lambda elapsed_time, max_time: elapsed_time > max_time),
        salience=10  
    )
    def time_limit_violation(self, state, elapsed_time, max_time):
        self.retract(state)


    @Rule(
        AS.state1
        << State(
            left=MATCH.left1,
            right=MATCH.right1,
            flashlight_location=MATCH.flashlight_location1,
            elapsed_time=MATCH.elapsed_time1,
            path=MATCH.path1,
            depth=MATCH.depth1,
            sequence=MATCH.sequence1,
        ),
        AS.state2
        << State(
            left=MATCH.left2,
            right=MATCH.right2,
            flashlight_location=MATCH.flashlight_location2,
            elapsed_time=MATCH.elapsed_time2,
            path=MATCH.path2,
            depth=MATCH.depth2,
            sequence=MATCH.sequence2,
        ),
        TEST(lambda state1, state2: state1 != state2),
        TEST(
            lambda left1, right1, flashlight_location1, left2, right2, flashlight_location2, elapsed_time1, elapsed_time2:
            left1 == left2 and right1 == right2 and flashlight_location1 == flashlight_location2 and
            elapsed_time1 >= elapsed_time2  
        ),
        salience=9
    )
    def duplicate_state_elimination(self, state1, elapsed_time1, elapsed_time2):
        self.retract(state1)


    @Rule(
        AS.state
        << State(
            left=MATCH.left,
            right=MATCH.right,
            flashlight_location=MATCH.flashlight_location,
            elapsed_time=MATCH.elapsed_time,
            path=MATCH.path,
            depth=MATCH.depth,
            sequence=MATCH.sequence,
        ),
        TEST(
            lambda left, right, flashlight_location: (
                flashlight_location == "left" and not left
            )
            or (flashlight_location == "right" and not right)
        ),
        salience=8  
    )
    def flashlight_violation(self, state, left, right, flashlight_location):
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
            sequence=MATCH.sequence,
        ),
        TEST(
            lambda path: path and path[-1][0] == "cross" and len(
                path[-1][1]) > 2
        ),
        salience=8 
    )
    def bridge_capacity_violation(self, state, path):
        last_move = path[-1]
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
            sequence=MATCH.sequence,
        ),
        TEST(
            lambda path: path and (
                (path[-1][0] == "cross" and len(path[-1][1]) < 2)
                or (path[-1][0] == "return" and len(path[-1][1]) != 1)
            )
        ),
        salience=8 
    )
    def invalid_move_pattern(self, state, path):
        last_move = path[-1]
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
            sequence=MATCH.sequence,
        ),
        TEST(
            lambda path, flashlight_location: path and (
                (path[-1][0] == "cross" and flashlight_location != "right")
                or (path[-1][0] == "return" and flashlight_location != "left")
            )
        ),
        salience=8  
    )
    def flashlight_location_inconsistency(self, state, path, flashlight_location):
        last_move = path[-1]
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
            sequence=MATCH.sequence,
        ),
        VisitedState(
            left=MATCH.left,
            right=MATCH.right,
            flashlight_location=MATCH.flashlight_location,
            best_time=MATCH.best_time,
        ),
        TEST(lambda elapsed_time, best_time: elapsed_time > best_time),
        salience=11  
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
            sequence=MATCH.sequence,
        ),
        AS.visited
        << VisitedState(
            left=MATCH.left,
            right=MATCH.right,
            flashlight_location=MATCH.flashlight_location,
            best_time=MATCH.best_time,
        ),
        TEST(lambda elapsed_time, best_time: elapsed_time <= best_time),
        salience=12  # Even higher salience for updating best time
    )
    def update_best_time(self, visited, left, right, flashlight_location, elapsed_time):
        (visited in self.facts) and self.retract(visited)
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
            depth=MATCH.depth,
            sequence=MATCH.sequence,
        ),
        TimeConstraint(max_time=MATCH.max_time),
        TEST(lambda left: not left),
        TEST(lambda right: len(right) == 4),
        TEST(lambda elapsed_time, max_time: elapsed_time <= max_time),
        NOT(Solution(moves=MATCH.path, total_time=MATCH.elapsed_time)),
        TEST(lambda path: path is not None and len(path) > 0),
        salience=5,  
    )
    def goal_reached(self, state, elapsed_time, path):
        solution_signature = tuple(
            (action, tuple(people), time_taken) for action, people, time_taken in path
        )



        self.solution_signatures.add(solution_signature)
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
        (state in self.facts) and self.retract(state)

    @Rule(
        AS.solution
        << Solution(
            moves=MATCH.moves,
            total_time=MATCH.total_time,
            solution_id=MATCH.solution_id,
        ),
        NOT(SolutionPrinted(solution_id=MATCH.solution_id)),
        salience=1  
    )
    def print_solution(self, moves, total_time, solution_id):
        print(f"{'='*60}")
        print(
            f"\033[1mSOLUTION {solution_id} FOUND (Total time: {total_time} minutes):\033[0m"
        )
        print("=" * 60)
        for i, move in enumerate(moves, 1):
            action, people, time_taken = move
            action_handlers = {
                "cross": lambda: self.handle_cross_action(i, people, time_taken),
                "return": lambda: self.handle_return_action(i, people, time_taken),
            }
            action_handlers.get(action, lambda: None)()

        print("-" * 60)
        print(
            f"\033[32mSUCCESS: All 4 people crossed in {total_time} minutes!\033[0m")
        print("=" * 60)
        print("")
        self.declare(SolutionPrinted(solution_id=solution_id))

    def handle_cross_action(self, step, people, time_taken):
        actions = {
            2: lambda: print(
                f"\033[31mStep {step}:\033[0m {people[0]} and {people[1]} cross together ⨠ \033[34m{time_taken} minutes\033[0m"
            ),
            1: lambda: print(
                f"\033[31mStep {step}:\033[0m {people[0]} crosses alone ⨠ \033[34m{time_taken} minutes\033[0m"
            ),
        }
        actions.get(
            len(people),
            lambda: print(
                f"\033[31mStep {step}:\033[0m {', '.join(people)} cross together ⨠ \033[34m{time_taken} minutes\033[0m"
            ),
        )()

    def handle_return_action(self, step, people, time_taken):
        print(
            f"\033[31mStep {step}:\033[0m {people[0]} returns with flashlight ⨠ \033[34m{time_taken} minutes\033[0m"
        )
