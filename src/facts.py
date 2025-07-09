from experta import Fact, Field

class State(Fact):
    left = Field(list)
    right = Field(list)
    flashlight_location = Field(str)
    elapsed_time = Field(float)
    path = Field(list)
    depth = Field(int)
    sequence = Field(int,mandatory=False) 

class TimeConstraint(Fact):
    max_time = Field(float)

class ValidTimeWindow(Fact):
    state_ref = Field(object)
    elapsed_time = Field(float)

class SufficientPeople(Fact):
    state_ref = Field(object)
    side = Field(str)
    count = Field(int)

class ValidMoveCondition(Fact):
    state_ref = Field(object)
    move_type = Field(str)
    left = Field(list)
    right = Field(list)
    elapsed_time = Field(float)
    path = Field(list)
    depth = Field(int)
    sequence = Field(int)  

class PotentialState(Fact):
    left = Field(list)
    right = Field(list)
    flashlight_location = Field(str)
    elapsed_time = Field(float)
    path = Field(list)
    depth = Field(int)
    move_type = Field(str)

class VisitedState(Fact):
    left = Field(list)
    right = Field(list)
    flashlight_location = Field(str)
    best_time = Field(float)

class StateToRetract(Fact):
    state_ref = Field(object)
    violation_type = Field(str)
    details = Field(str)

class RetractionRequest(Fact):
    state_signature = Field(tuple)
    reason = Field(str)

class Solution(Fact):
    moves = Field(list)
    total_time = Field(float)
    solution_id = Field(int)

class SolutionPrinted(Fact):
    solution_id = Field(int)

class SearchAlgorithm(Fact):
    algorithm = "bfs"

class ProcessedState(Fact):
    sequence = Field(int)

class ActiveState(Fact):
    state_ref = Field(object)

class BFSQueue(Fact):
    current_depth = Field(int)
    processing_depth = Field(int)