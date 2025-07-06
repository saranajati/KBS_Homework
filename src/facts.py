from experta import Fact, Field
import collections
import collections.abc
collections.Mapping = collections.abc.Mapping

# Optimized core state - combines position and path tracking


class State(Fact):
    left = Field(list, mandatory=True)           # People on left side
    right = Field(list, mandatory=True)          # People on right side
    flashlight_location = Field(str, mandatory=True)  # "left" or "right"
    elapsed_time = Field(float, mandatory=True)   # Total time elapsed
    path = Field(list, mandatory=True)           # Complete move history
    depth = Field(int, default=0)               # Search depth

# Optimized visited state tracking - prevents revisiting worse paths


class VisitedState(Fact):
    left = Field(list, mandatory=True)
    right = Field(list, mandatory=True)
    flashlight_location = Field(str, mandatory=True)
    best_time = Field(float, mandatory=True)    # Best time to reach this state

# Move printing - separates cross and return actions


class PrintMove(Fact):
    step = Field(int, mandatory=True)
    action = Field(str, mandatory=True)  # "cross" or "return"
    people = Field(tuple, mandatory=True)
    time = Field(float, mandatory=True)

# Solution tracking - final result


class Solution(Fact):
    moves = Field(list, mandatory=True)
    total_time = Field(float, mandatory=True)
    is_valid = Field(bool, default=True)
