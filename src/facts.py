from experta import Fact, Field


class State(Fact):
    """Game state with BFS ordering support"""
    left = Field(list)
    right = Field(list)
    flashlight_location = Field(str)
    elapsed_time = Field(float)
    path = Field(list)
    depth = Field(int)
    sequence = Field(int,mandatory=False)  # NEW: For BFS ordering


class TimeConstraint(Fact):
    """Time limit constraint"""
    max_time = Field(float)


class ValidTimeWindow(Fact):
    """Marks states within valid time window"""
    state_ref = Field(object)
    elapsed_time = Field(float)


class SufficientPeople(Fact):
    """Marks states with sufficient people to make moves"""
    state_ref = Field(object)
    side = Field(str)
    count = Field(int)


class ValidMoveCondition(Fact):
    """Indicates valid move conditions exist"""
    state_ref = Field(object)
    move_type = Field(str)
    left = Field(list)
    right = Field(list)
    elapsed_time = Field(float)
    path = Field(list)
    depth = Field(int)
    sequence = Field(int)  # NEW


class PotentialState(Fact):
    """Potential new state before validation"""
    left = Field(list)
    right = Field(list)
    flashlight_location = Field(str)
    elapsed_time = Field(float)
    path = Field(list)
    depth = Field(int)
    move_type = Field(str)


class VisitedState(Fact):
    """Tracks visited states for pruning"""
    left = Field(list)
    right = Field(list)
    flashlight_location = Field(str)
    best_time = Field(float)


class StateToRetract(Fact):
    """Marks states for retraction due to constraint violations"""
    state_ref = Field(object)
    violation_type = Field(str)
    details = Field(str)


class RetractionRequest(Fact):
    """Request to retract a state"""
    state_signature = Field(tuple)
    reason = Field(str)


class Solution(Fact):
    """Found solution"""
    moves = Field(list)
    total_time = Field(float)
    solution_id = Field(int)


class SolutionPrinted(Fact):
    """Marks that a solution has been printed"""
    solution_id = Field(int)



class SearchAlgorithm(Fact):
    algorithm = "bfs"


# NEW: BFS Control Facts
class ProcessedState(Fact):
    """Mark that a state has been processed"""
    sequence = Field(int)


class ActiveState(Fact):
    """Mark the currently active state being processed"""
    state_ref = Field(object)


class BFSQueue(Fact):
    """Maintains BFS queue state"""
    current_depth = Field(int)
    processing_depth = Field(int)




