from experta import Fact, Field
import collections
import collections.abc
collections.Mapping = collections.abc.Mapping




class State(Fact):
    left = Field(list, mandatory=True)           # People on left side
    right = Field(list, mandatory=True)          # People on right side
    flashlight_location = Field(str, mandatory=True)  # "left" or "right"
    elapsed_time = Field(float, mandatory=True)   # Total time elapsed
    path = Field(list, mandatory=True)           # Complete move history
    depth = Field(int, default=0)               # Search depth



class VisitedState(Fact):
    left = Field(list, mandatory=True)
    right = Field(list, mandatory=True)
    flashlight_location = Field(str, mandatory=True)
    best_time = Field(float, mandatory=True)    # Best time to reach this state



class PrintMove(Fact):
    step = Field(int, mandatory=True)
    action = Field(str, mandatory=True)  # "cross" or "return"
    people = Field(tuple, mandatory=True)
    time = Field(float, mandatory=True)



class Solution(Fact):
    moves = Field(list, mandatory=True)
    total_time = Field(float, mandatory=True)
    is_valid = Field(bool, default=True)

# Additional Fact classes for constraint checking

class TimeConstraint(Fact):
    max_time = Field(float, mandatory=True)

class PotentialState(Fact):
    left = Field(list, mandatory=True)
    right = Field(list, mandatory=True)
    flashlight_location = Field(str, mandatory=True)
    elapsed_time = Field(float, mandatory=True)
    path = Field(list, mandatory=True)
    depth = Field(int, mandatory=True)
    move_type = Field(str, mandatory=True)  # "cross" or "return"

class RetractionRequest(Fact):
    state_signature = Field(tuple, mandatory=True)
    reason = Field(str, mandatory=True)

class ConstraintViolation(Fact):
    violation_type = Field(str, mandatory=True)
    details = Field(str, mandatory=True)

class StateToRetract(Fact):
    state_ref = Field(object, mandatory=True)
    violation_type = Field(str, mandatory=True)
    details = Field(str, mandatory=True)

class ValidTimeWindow(Fact):
    state_ref = Field(object, mandatory=True)
    elapsed_time = Field(float, mandatory=True)

class SufficientPeople(Fact):
    state_ref = Field(object, mandatory=True)
    side = Field(str, mandatory=True)  # "left" or "right"
    count = Field(int, mandatory=True)

class ValidMoveCondition(Fact):
    state_ref = Field(object, mandatory=True)
    move_type = Field(str, mandatory=True)  # "cross" or "return"
    left = Field(list, mandatory=True)
    right = Field(list, mandatory=True)
    elapsed_time = Field(float, mandatory=True)
    path = Field(list, mandatory=True)
    depth = Field(int, mandatory=True)
