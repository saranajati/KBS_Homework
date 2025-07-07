from experta import Fact

# State representation


class State(Fact):
    """Represents a state of the bridge puzzle"""
    left = None          # People on left side
    right = None         # People on right side
    flashlight_location = None  # "left" or "right"
    elapsed_time = None  # Total time elapsed
    path = None          # List of moves taken
    depth = None         # Search depth

# Potential state (before validation)


class PotentialState(Fact):
    """Represents a potential state before validation"""
    left = None
    right = None
    flashlight_location = None
    elapsed_time = None
    path = None
    depth = None
    move_type = None     # "cross" or "return"

# Solution representation


class Solution(Fact):
    """Represents a found solution"""
    moves = None         # List of moves
    total_time = None    # Total time taken
    solution_id = None   # Unique identifier for the solution

# Track printed solutions


class SolutionPrinted(Fact):
    """Tracks which solutions have been printed"""
    solution_id = None

# Constraints


class TimeConstraint(Fact):
    """Time constraint for the puzzle"""
    max_time = None

# State tracking


class VisitedState(Fact):
    """Tracks visited states with best time"""
    left = None
    right = None
    flashlight_location = None
    best_time = None

# Validation markers


class ValidTimeWindow(Fact):
    """Marks states within valid time window"""
    state_ref = None
    elapsed_time = None


class SufficientPeople(Fact):
    """Marks states with sufficient people for moves"""
    state_ref = None
    side = None          # "left" or "right"
    count = None


class ValidMoveCondition(Fact):
    """Marks states with valid move conditions"""
    state_ref = None
    move_type = None     # "cross" or "return"
    left = None
    right = None
    elapsed_time = None
    path = None
    depth = None

# Constraint violations


class StateToRetract(Fact):
    """Marks states for retraction due to constraint violations"""
    state_ref = None
    violation_type = None
    details = None


class RetractionRequest(Fact):
    """Requests retraction of a state"""
    state_signature = None
    reason = None

# Print management


class PrintMove(Fact):
    """Manages printing of solution moves"""
    step = None
    action = None
    people = None
    time = None

# BFS & DFS

class SearchAlgorithm(Fact):
    algorithm = "bfs"
