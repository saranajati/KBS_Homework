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

        facts_to_retract = filter(lambda fact: isinstance(fact, (State, VisitedState, ReadyToProcess, ProcessedState, BFSQueue)), list(self.facts))
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
        AS.state << State(
            left=MATCH.left,
            right=MATCH.right,
            flashlight_location=MATCH.flashlight_location,
            elapsed_time=MATCH.elapsed_time,
            path=MATCH.path,
            depth=MATCH.depth,
            sequence=MATCH.sequence,
        ),
        TimeConstraint(max_time=MATCH.max_time),
        TEST(lambda elapsed_time, max_time: elapsed_time <= max_time),
        NOT(
            VisitedState(
                left=MATCH.left,
                right=MATCH.right,
                flashlight_location=MATCH.flashlight_location,
            )
        ),
    )
    def mark_unvisited_state(self, state, left, right, flashlight_location, elapsed_time):
        """Mark state as visited and ready for processing"""
        self.declare(
            VisitedState(
                left=left,
                right=right,
                flashlight_location=flashlight_location,
                best_time=elapsed_time,
            )
        )
        self.declare(ReadyToProcess(state_ref=state))

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
        self.declare(ReadyToProcess(state_ref=state))

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
        if state in self.facts:
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
        ReadyToProcess(state_ref=MATCH.state_ref),
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

                # Create new state with sequence
                new_left = [
                    p for p in left_list if p not in [person1, person2]]
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

                if new_depth > current_depth:
                    if queue in self.facts:
                        self.retract(queue)
                    self.declare(BFSQueue(current_depth=new_depth,
                                 processing_depth=current_depth))

        # Mark this state as processed
        self.declare(ProcessedState(sequence=sequence))

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
        ReadyToProcess(state_ref=MATCH.state_ref),
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
            new_right = [p for p in right_list if p != person]
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

            if new_depth > current_depth:
                if queue in self.facts:
                    self.retract(queue)
                self.declare(BFSQueue(current_depth=new_depth,
                             processing_depth=current_depth))

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
        unprocessed_states = [f for f in self.facts if isinstance(
            f, State) and hasattr(f, 'depth') and f.depth == processing_depth]
        processed_sequences = [
            f.sequence for f in self.facts if isinstance(f, ProcessedState)]

        if all(hasattr(state, 'sequence') and state.sequence in processed_sequences for state in unprocessed_states):
            new_processing_depth = processing_depth + 1
            # Only retract if queue still exists in facts
            if queue in self.facts:
                self.retract(queue)
            self.declare(BFSQueue(current_depth=queue['current_depth'],
                         processing_depth=new_processing_depth))
            print(
                f"\n🔄 BFS: Advancing to process depth {new_processing_depth}")

    @Rule(
        AS.ready << ReadyToProcess(state_ref=MATCH.state_ref),
        AS.processed << ProcessedState(sequence=MATCH.sequence),
        TEST(lambda state_ref, sequence: hasattr(
            state_ref, 'sequence') and state_ref.sequence == sequence),
    )
    def cleanup_processing_markers(self, ready, processed):
        """Clean up processing markers"""
        if ready in self.facts:
            self.retract(ready)
        if processed in self.facts:
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
        ReadyToProcess(state_ref=MATCH.state_ref),
        TEST(lambda state_ref, state: state_ref == state),
        TEST(lambda depth: depth > 0),
        TEST(lambda path: path is not None and len(path) > 0),
    )
    def log_search_progress(self, left, right, flashlight_location, elapsed_time, path, depth, sequence):
        """Log search progress"""
        last_action = path[-1]
        action, people, time_taken = last_action
        people_str = ", ".join(people)
        print(
            f"⟬BFS Level {depth} (seq:{sequence})⟭ {action}: {people_str}")
        print(f"\033[31m⬅️  Left: {list(left)}\033[0m")
        print(f"\033[34m➡️  Right: {list(right)}\033[0m")
        print(
            f"\033[33m🔦  Flashlight: {flashlight_location}\033[0m   \033[32m⏱️  Time: {elapsed_time}\033[0m")
        print("")

   