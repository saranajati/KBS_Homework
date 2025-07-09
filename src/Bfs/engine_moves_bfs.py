from facts import *
from experta import *
import collections
import collections.abc
collections.Mapping = collections.abc.Mapping


class BridgePuzzleSolverMovesBfs(KnowledgeEngine):
    def __init__(self, people, max_time=17):
        super().__init__()
        self.people = {name: float(time) for name, time in people}
        self.max_time = float(max_time)
        self.solutions = []
        self.solution_count = 0
        self.sequence_counter = 0  # NEW: Track sequence for BFS ordering

    @Rule()
    def initialize(self):
        left_side = list(self.people.keys())
        self.sequence_counter += 1

        facts_to_retract = filter(lambda fact: isinstance(
            fact, (State, VisitedState, ActiveState, ProcessedState, BFSQueue)), list(self.facts))
        for fact in facts_to_retract:
            self.retract(fact)

        self.declare(
            State(
                left=left_side,
                right=[],
                flashlight_location="left",
                elapsed_time=0.0,
                path=[],
                depth=0,
                sequence=self.sequence_counter,
            )
        )
        self.declare(TimeConstraint(max_time=17.0))
        self.declare(BFSQueue(current_depth=0, processing_depth=0))

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
        OR(
            NOT(
                VisitedState(
                    left=MATCH.left,
                    right=MATCH.right,
                    flashlight_location=MATCH.flashlight_location,
                )
            ),
            AND(
                VisitedState(
                    left=MATCH.left,
                    right=MATCH.right,
                    flashlight_location=MATCH.flashlight_location,
                    best_time=MATCH.best_time,
                ),
                TEST(
                    lambda elapsed_time, best_time: best_time is None
                    or elapsed_time <= best_time
                ),
            ),
        ),
        TimeConstraint(max_time=MATCH.max_time),
        TEST(lambda elapsed_time, max_time: elapsed_time <= max_time),
    )
    def mark_unvisited_state(
        self, state, left, right, flashlight_location, elapsed_time
    ):
        """Mark state as visited and ready for processing"""
        self.declare(
            VisitedState(
                left=left,
                right=right,
                flashlight_location=flashlight_location,
                best_time=elapsed_time,
            )
        )
        self.declare(ActiveState(state_ref=state))

    @Rule(
        AS.state << State(
            left=MATCH.left,
            right=MATCH.right,
            flashlight_location=MATCH.flashlight_location,
            elapsed_time=MATCH.elapsed_time,
            path=MATCH.path,
            depth=MATCH.depth,
            sequence=MATCH.sequence,
        ),
        AS.visited << VisitedState(
            left=MATCH.left,
            right=MATCH.right,
            flashlight_location=MATCH.flashlight_location,
            best_time=MATCH.best_time,
        ),
        TEST(lambda elapsed_time, best_time: elapsed_time < best_time),
    )
    def update_better_path(self, state, visited, left, right, flashlight_location, elapsed_time):
        """Update visited state with better time"""
        self.retract(visited)
        self.declare(
            VisitedState(
                left=left,
                right=right,
                flashlight_location=flashlight_location,
                best_time=elapsed_time,
            )
        )
        self.declare(ActiveState(state_ref=state))

    @Rule(
        AS.state << State(
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
    )
    def prune_worse_path(self, state):
        """Remove states with worse times"""
        self.retract(state)

    @Rule(
        AS.queue << BFSQueue(current_depth=MATCH.current_depth,
                             processing_depth=MATCH.processing_depth),
        AS.state << State(
            left=MATCH.left,
            right=MATCH.right,
            flashlight_location="left",
            elapsed_time=MATCH.elapsed_time,
            path=MATCH.path,
            depth=MATCH.depth,
            sequence=MATCH.sequence,
        ),
        ActiveState(state_ref=MATCH.state_ref),
        TEST(lambda state_ref, state: state_ref == state),
        TEST(lambda depth, processing_depth: depth == processing_depth),
        TEST(lambda left: len(left) >= 2),
        TEST(lambda sequence: sequence is not None),
    )
    def generate_cross_moves(self, state, queue, left, right, elapsed_time, path, depth, current_depth, sequence):
        """Generate all possible cross moves from left to right"""
        left_list = list(left)
        right_list = list(right)

        for i in range(len(left_list)):
            for j in range(i + 1, len(left_list)):
                person1, person2 = left_list[i], left_list[j]
                crossing_time = max(self.people[person1], self.people[person2])
                new_time = elapsed_time + crossing_time

                new_left = list(filter(lambda p: p not in [
                                person1, person2], left_list))
                new_right = sorted(right_list + [person1, person2])
                new_path = list(path) + \
                    [("cross", (person1, person2), crossing_time)]

                self.sequence_counter += 1
                new_depth = depth + 1

                self.declare(
                    State(
                        left=new_left,
                        right=new_right,
                        flashlight_location="right",
                        elapsed_time=new_time,
                        path=new_path,
                        depth=new_depth,
                        sequence=self.sequence_counter,
                    )
                )

                (new_depth > current_depth) and self._update_bfs_queue(
                    queue, new_depth, current_depth)

        # Mark this state as processed
        self.declare(ProcessedState(sequence=sequence))

    def _update_bfs_queue(self, queue, new_depth, current_depth):
        """Helper method to update BFS queue"""
        (queue in self.facts) and self.retract(queue)
        self.declare(BFSQueue(current_depth=new_depth,
                     processing_depth=current_depth))
        return True

    @Rule(
        AS.queue << BFSQueue(current_depth=MATCH.current_depth,
                             processing_depth=MATCH.processing_depth),
        AS.state << State(
            left=MATCH.left,
            right=MATCH.right,
            flashlight_location="right",
            elapsed_time=MATCH.elapsed_time,
            path=MATCH.path,
            depth=MATCH.depth,
            sequence=MATCH.sequence,
        ),
        ActiveState(state_ref=MATCH.state_ref),
        TEST(lambda state_ref, state: state_ref == state),
        TEST(lambda depth, processing_depth: depth == processing_depth),
        TEST(lambda right: len(right) >= 1),
        TEST(lambda left: len(left) > 0),
        TEST(lambda sequence: sequence is not None),
    )
    def generate_return_moves(self, state, queue, left, right, elapsed_time, path, depth, current_depth, sequence):
        """Generate all possible return moves from right to left"""
        left_list = list(left)
        right_list = list(right)

        for person in right_list:
            crossing_time = self.people[person]
            new_time = elapsed_time + crossing_time

            # Create new state with sequence
            new_left = sorted(left_list + [person])
            new_right = list(filter(lambda p: p != person, right_list))
            new_path = list(path) + [("return", (person,), crossing_time)]

            self.sequence_counter += 1
            new_depth = depth + 1

            self.declare(
                State(
                    left=new_left,
                    right=new_right,
                    flashlight_location="left",
                    elapsed_time=new_time,
                    path=new_path,
                    depth=new_depth,
                    sequence=self.sequence_counter,
                )
            )

            (new_depth > current_depth) and self._update_bfs_queue(
                queue, new_depth, current_depth)

        # Mark this state as processed
        self.declare(ProcessedState(sequence=sequence))

    @Rule(
        AS.queue << BFSQueue(current_depth=MATCH.current_depth,
                             processing_depth=MATCH.processing_depth),
        TEST(lambda processing_depth,
             current_depth: processing_depth < current_depth),
    )
    def advance_bfs_level(self, queue, processing_depth):
        """Advance to next BFS level when current level is complete"""
        unprocessed_states = list(filter(
            lambda f: isinstance(f, State) and hasattr(
                f, 'depth') and f.depth == processing_depth,
            self.facts
        ))
        processed_sequences = list(map(
            lambda f: f.sequence,
            filter(lambda f: isinstance(f, ProcessedState), self.facts)
        ))

        all_processed = all(hasattr(
            state, 'sequence') and state.sequence in processed_sequences for state in unprocessed_states)
        all_processed and self._advance_to_next_level(queue, processing_depth)

    def _advance_to_next_level(self, queue, processing_depth):
        """Helper method to advance to next BFS level"""
        new_processing_depth = processing_depth + 1
        (queue in self.facts) and self.retract(queue)
        self.declare(BFSQueue(
            current_depth=queue['current_depth'], processing_depth=new_processing_depth))
        print(
            f"\033[1m⚙️  BFS: Advancing to process depth {new_processing_depth}\033[0m\n"
        )
        return True

    @Rule(
        AS.ready << ActiveState(state_ref=MATCH.state_ref),
        AS.processed << ProcessedState(sequence=MATCH.sequence),
        TEST(lambda state_ref, sequence: hasattr(
            state_ref, 'sequence') and state_ref.sequence == sequence),
    )
    def cleanup_processing_markers(self, ready, processed):
        """Clean up processing markers"""
        self.retract(ready)
        self.retract(processed)

    @Rule(
        AS.state << State(
            left=MATCH.left,
            right=MATCH.right,
            flashlight_location=MATCH.flashlight_location,
            elapsed_time=MATCH.elapsed_time,
            path=MATCH.path,
            depth=MATCH.depth,
            sequence=MATCH.sequence,
        ),
        ActiveState(state_ref=MATCH.state_ref),
        TEST(lambda state_ref, state: state_ref == state),
        TEST(lambda depth: depth > 0),
        TEST(lambda path: path is not None and len(path) > 0),
    )
    def log_search_progress(
        self, left, right, flashlight_location, elapsed_time, path, depth, sequence
    ):
        last_action = path[-1]
        action, people, time_taken = last_action
        people_str = ", ".join(people)
        print(f"⟬BFS Level {depth} (seq:{sequence})⟭ {action}: {people_str}")
        print(
            f"\033[31m⬅️  Left: {list(left)}\033[0m   \033[34m➡️  Right: {list(right)}\033[0m"
        )
        print(
            f"\033[33m🔦  Flashlight: {flashlight_location}\033[0m   \033[32m⏱️  Time: {elapsed_time}\033[0m"
        )
        print("")

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
