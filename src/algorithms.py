from facts import *
from experta import *
from engine import *


class BridgePuzzleAlgorithms(KnowledgeEngine):
    def __init__(self, people, max_time=17):
        super().__init__()
        self.people = {name: float(time) for name, time in people}
        self.max_time = float(max_time)

    @DefFacts()
    def trigger(self):
        yield Fact("start")

    @Rule(Fact("start"), SearchAlgorithm(name="bfs"))
    def use_bfs(self):
        print("\n🔍 Using BFS...\n")
        solver = BridgePuzzleAlgorithmsLogic(self.people, self.max_time)
        solver.reset()
        solver.declare(
            State(
                left=list(self.people.keys()),
                right=[],
                flashlight_location="left",
                elapsed_time=0.0,
                path=[],
            )
        )
        solver.declare(TimeConstraint(max_time=self.max_time))
        solver.declare(SearchAlgorithm(name="bfs"))
        solver.run()
        solver.print_search_tree()
        #   solver.print_final_summary()
        self.halt()

    @Rule(Fact("start"), SearchAlgorithm(name="dfs"))
    def use_dfs(self):
        print("\n🔎 Using DFS...\n")
        solver = BridgePuzzleAlgorithmsLogic(self.people, self.max_time)
        solver.reset()
        solver.declare(
            State(
                left=list(self.people.keys()),
                right=[],
                flashlight_location="left",
                elapsed_time=0.0,
                path=[],
            )
        )
        solver.declare(TimeConstraint(max_time=self.max_time))
        solver.declare(SearchAlgorithm(name="dfs"))
        solver.run()
        solver.print_search_tree()
        #   solver.print_final_summary()
        self.halt()


# search_logic
class BridgePuzzleAlgorithmsLogic(KnowledgeEngine):
    def __init__(self, people, max_time=17):
        super().__init__()
        self.people = people
        self.max_time = float(max_time)
        self.generated_states = set()  # to avoid duplicates
        self.search_tree = []
        self.found = False

    def check_state(self, state: State):
        return (
            tuple(sorted(state["left"])),
            tuple(sorted(state["right"])),
            state["flashlight_location"],
            int(state["elapsed_time"]),
        )

    @Rule(
        State(
            left=MATCH.left,
            right=MATCH.right,
            flashlight_location="right",
            elapsed_time=MATCH.time,
            path=MATCH.path,
        ),
        TEST(lambda right: len(right) >= 1),
        SearchAlgorithm(name=MATCH.name),
        salience=100,
    )
    def return_one_person(self, left, right, time, path, name):
        #   for person in right:
        #       new_time = time + self.people[person]
        #       if new_time > self.max_time:
        #           continue
        for person in right:
            return_time = self.people[person]
            new_time = time + return_time
            if new_time > self.max_time:
                continue
            new_left = list(left) + [person]
            new_right = list(right)
            new_right.remove(person)
            new_path = list(path) + [f"{person} returns ← ({self.people[person]} min)"]
            new_state = State(
                left=new_left,
                right=new_right,
                flashlight_location="left",
                elapsed_time=new_time,
                path=new_path,
            )
            sid = self.check_state(new_state)
            if sid not in self.generated_states:
                self.generated_states.add(sid)
                self.insert_with_algo(new_state, name)

    @Rule(
        State(
            left=MATCH.left,
            right=MATCH.right,
            flashlight_location="left",
            elapsed_time=MATCH.time,
            path=MATCH.path,
        ),
        TEST(lambda left: len(left) >= 1),
        SearchAlgorithm(name=MATCH.name),
        salience=90,
    )
    def cross_one_person(self, left, right, time, path, name):
        for person in left:
            t = self.people[person]
            new_time = time + t
            if new_time > self.max_time:
                continue
            new_left = list(left)
            new_left.remove(person)
            new_right = list(right) + [person]
            new_path = list(path) + [f"{person} crosses alone → ({t} min)"]
            new_state = State(
                left=new_left,
                right=new_right,
                flashlight_location="right",
                elapsed_time=new_time,
                path=new_path,
            )
            sid = self.check_state(new_state)
            if sid not in self.generated_states:
                self.generated_states.add(sid)
                self.insert_with_algo(new_state, name)

    @Rule(
        State(
            left=MATCH.left,
            right=MATCH.right,
            flashlight_location="left",
            elapsed_time=MATCH.time,
            path=MATCH.path,
        ),
        TEST(lambda left: len(left) >= 2),
        SearchAlgorithm(name=MATCH.name),
        salience=100,
    )
    def cross_two_people(self, left, right, time, path, name):
        for i in range(len(left)):
            for j in range(i + 1, len(left)):
                p1, p2 = left[i], left[j]
                t = max(self.people[p1], self.people[p2])
                new_time = time + t
                if new_time > self.max_time:
                    continue

                new_left = list(left)
                new_left.remove(p1)
                new_left.remove(p2)
                new_right = list(right) + [p1, p2]
                new_path = list(path) + [f"{p1} & {p2} cross → ({t} min)"]

                new_state = State(
                    left=new_left,
                    right=new_right,
                    flashlight_location="right",
                    elapsed_time=new_time,
                    path=new_path,
                )
                sid = self.check_state(new_state)
                if sid not in self.generated_states:
                    self.generated_states.add(sid)
                    self.insert_with_algo(new_state, name)

    @Rule(
        State(
            left=MATCH.left,
            right=MATCH.right,
            flashlight_location="right",
            elapsed_time=MATCH.time,
            path=MATCH.path,
        ),
        TEST(lambda left: len(left) == 1),
        SearchAlgorithm(name=MATCH.name),
        salience=80,
    )
    def bring_last_person(self, left, right, time, path, name):
        person = list(left)[0]
        t = self.people[person]
        new_time = time + t
        if new_time > self.max_time:
            return

        new_left = []
        new_right = list(right) + [person]
        new_path = list(path) + [f"{person} crosses alone (final) → ({t} min)"]

        new_state = State(
            left=new_left,
            right=new_right,
            flashlight_location="right",
            elapsed_time=new_time,
            path=new_path,
        )
        sid = self.check_state(new_state)
        if sid not in self.generated_states:
            self.generated_states.add(sid)
            self.insert_with_algo(new_state, name)

    @Rule(
        State(
            left=MATCH.left,
            right=MATCH.right,
            flashlight_location="left",
            elapsed_time=MATCH.time,
            path=MATCH.path,
        ),
        TEST(lambda left: len(left) >= 1),
        SearchAlgorithm(name=MATCH.name),
        salience=85,
    )
    def return_one_person_from_left(self, left, right, time, path, name):
        for person in left:
            t = self.people[person]
            new_time = time + t
            if new_time > self.max_time:
                continue

            new_left = list(left)
            new_left.remove(person)
            new_right = list(right) + [person]
            new_path = list(path) + [f"{person} crosses back ← ({t} min)"]

            new_state = State(
                left=new_left,
                right=new_right,
                flashlight_location="right",
                elapsed_time=new_time,
                path=new_path,
            )
            sid = self.check_state(new_state)
            if sid not in self.generated_states:
                self.generated_states.add(sid)
                self.insert_with_algo(new_state, name)

    @Rule(
        State(
            left=MATCH.left,
            right=MATCH.right,
            flashlight_location=MATCH.light,
            elapsed_time=MATCH.time,
            path=MATCH.path,
        ),
        TEST(lambda left, time: len(left) == 0 and time <= 17.0),
        salience=200,
    )
    def goal_reached(self, time, path):
        if not self.found:
            self.found = True
            print(f"\033[1mSOLUTION FOUND (Total time: {time} minutes):\033[0m")
            print("=" * 60)
            for step in path:
                print("   ◉", step)
            print(f"{'='*60}")
            print(f"\033[32m✅ SUCCESS: All 4 people crossed in {time} minutes!\033[0m")
            self.halt()

    def insert_with_algo(self, state_fact, name):
        self.search_tree.append(state_fact)  # حفظ الحالة في الشجرة
        self.declare(state_fact)
        if name == "dfs":
            # DFS expands immediately (simulated by higher salience)
            self.declare(state_fact)
        elif name == "bfs":
            # In BFS we simulate queue via delayed rule re-fire (default salience)
            self.declare(state_fact)

    def print_search_tree(self):
        print(f"\n\033[1mSearch Tree (All Generated States):\033[0m")
        for idx, state in enumerate(self.search_tree, 1):
            print(f"\033[35mNode {idx}:\033[0m")
            print(f"\033[31m⬅️   Left:  {sorted(state['left'])}\033[0m")
            print(f"\033[34m➡️   Right: {sorted(state['right'])}\033[0m")
            print(
                f"\033[33m🔦  Flashlight: {state['flashlight_location']}\033[0m   \033[32m⏱️  Time:  {state['elapsed_time']} min\033[0m"
            )
            print(f"Path:")
            for step in state["path"]:
                print(f"   ◽ {step}")
            print("")

    def print_final_summary(self):
        print("\n✅ Final Result:")
        if not self.found:
            print("❌ No valid solution found within time limit.")
            return

        last_state = next(
            (
                s
                for s in self.search_tree
                if len(s["left"]) == 0 and s["flashlight_location"] == "right"
            ),
            None,
        )

        if last_state:
            print(f"🕒 Total Time: {last_state['elapsed_time']} minutes")
            print("📋 Solution Path:")
            for step in last_state["path"]:
                print(f"   - {step}")
        else:
            print("⚠️ Reached goal but could not retrieve solution path.")
