from experta import Fact, Field
import collections
import collections.abc
collections.Mapping = collections.abc.Mapping

# Facts for people and their crossing times


class Person(Fact):
    name = Field(str, mandatory=True)
    crossing_time = Field(int, mandatory=True)
    location = Field(str, default="left")  # "left" or "right"

# Facts for the bridge state


class BridgeState(Fact):
    left_side = Field(list, default=lambda: [])

    right_side = Field(list, default=lambda: [])
    flashlight_location = Field(str, default="left")
    time_elapsed = Field(int, default=0)
    moves_made = Field(list, default=lambda: [])

# Facts for the game state


class GameState(Fact):
    total_time_limit = Field(int, default=17)
    strategy = Field(str, default="bfs")
    current_depth = Field(int, default=0)
    max_depth = Field(int, default=50)

# Facts for move tracking


class Move(Fact):
    from_side = Field(str, mandatory=True)
    to_side = Field(str, mandatory=True)
    people = Field(list, mandatory=True)
    time_taken = Field(int, mandatory=True)
    move_number = Field(int, mandatory=True)

# Facts for solution tracking


class Solution(Fact):
    moves = Field(list, mandatory=True)
    total_time = Field(int, mandatory=True)
    is_valid = Field(bool, default=True)

# Facts for search state (for BFS/DFS)


class SearchState(Fact):
    state_id = Field(str, mandatory=True)
    parent_state = Field(str, default="")
    depth = Field(int, default=0)
    visited = Field(bool, default=False)
