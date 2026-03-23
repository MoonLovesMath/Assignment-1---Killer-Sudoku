"""
Back-tracking solver - combined backtracking + smart pruning

Improvements over naive solver:
    1. Precompute valid digit combination per cage
    2. MRV (Minimum Remaining Values) - picks the cell with fewest valid candidates
    3. Only try digits that are consistent with both peer values and cage combinations
"""

from itertools import combinations
from models import Cell, Cage, Grid


# Public solve
def solve(grid: Grid) -> bool:
    cage_combos = _precompute_cage_combos(grid)
    return _backtrack(grid, cage_combos)


def _precompute_cage_combos(grid: Grid) -> dict[int, list[tuple[int, ...]]]:
    """
    For each cage, compute all valid digit combinations:
        1. Use exactly 'cage.size' distinct digits from 1..N
        2. Their sum is 'cage.target'

    Returns: cage_id -> list of sorted digit tuples

    Example: cage of size 2, target=7, N=9: [(1,6), (2,5), (3, 4)]
    """

    combos: dict[int, list[tuple[int, ...]]] = {}
    digits = range(1, grid.n + 1)

    for cage in grid.cages:
        combos[cage.cage_id] = [
            combo 
            for combo in combinations(digits, cage.size)
            if sum(combo) == cage.target
        ]
    
    return combos


def _backtrack(grid: Grid, cage_combos: dict[int, list[tuple[int, ...]]]) -> bool:
    """Improved backtracking algorithm"""

    cell = _pick_cell(grid, cage_combos)

    if cell is None:
        return True
    
    for digit in _candidates(grid, cell, cage_combos):
        cell.value = digit

        if _is_consistent(grid, cell):
            if _backtrack(grid, cage_combos):
                return True
        
        cell.value = 0      # Backtrack

    return False


# MRV cell selection
def _pick_cell(grid: Grid, cage_combos: dict[int, list[tuple[int, ...]]]) -> Cell | None:
    """
    Minimum Remaining Values (MRV): pick the cell with fewest valid candidates. 
    """

    best_cell   = None
    best_count  = grid.n + 1

    for r in range(grid.n):
        for c in range(grid.n):
            cell = grid.cells[r][c]
            if cell.is_empty():
                count = len(_candidates(grid, cell, cage_combos))
                if count < best_count:
                    best_count  = count
                    best_cell   = cell
                    if count == 0:  # Dead end, returns best cel so far
                        return best_cell
    
    return best_cell


# Candidate generation
def _candidates(grid: Grid, cell: Cell, cage_combos: dict[int, list[tuple[int, ...]]]) -> list[int]:
    """
    Returns list of valid digits for this cell - intersection of:
        1. Digits still possible given the cage's valid combos
        2. Digits not already used by row/col/box peers
    """

    # Digits already placed in row/col/box peers
    peer_values = {p.value for p in grid.all_peers(cell.row, cell.col) if not p.is_empty()}

    # Digits already in cage
    cage = grid.get_cage(cell.row, cell.col)
    filled_in_cage = {c.value for c in cage.cells if not c.is_empty() and c is not cell}

    cage_allowed: set[int] = set()
    for combo in cage_combos[cage.cage_id]:
        combo_set = set(combo)
        if filled_in_cage.issubset(combo_set):
            cage_allowed |= combo_set - filled_in_cage

    return sorted(cage_allowed - peer_values)
"""
Tbf, this is one of the hardest-to-grasp piece of code
The intuition is as followed:
1. You want to find digits already used by row/col/box (d1) -> remove those from possible candidates
2. Find the digits in cage (d2) -> You want to choose possible combos for the cage, that has all of those digits in (d2)
3. Look into all possible (precomputed) digit combinations for the cage (D)
4. Call the list of possible candidates R (as in Result)
4. If (d2) is subset of (D), choose it, and R = union(R, D-d2), (D-d2) -> digits left to be filled
5. You don't want (d1) in (R) -> R = R - d1
"""


# ------------ Constraint checking ------------
def _is_consistent(grid: Grid, cell: Cell) -> bool:
    """Check if the grid is 'consistent' """
    return (_check_peers(grid, cell) and _check_cage(grid, cell))

def _check_peers(grid: Grid, cell: Cell) -> bool:
    """Returns False if any peer shares the same value"""
    for peer in grid.all_peers(cell.row, cell.col):
        if peer.value == cell.value:
            return False
    return True

def _check_cage(grid: Grid, cell: Cell) -> bool:
    """Returns False if the cage already has this digit or the sum is exceeded"""
    cage = grid.get_cage(cell.row, cell.col)
    return cage.is_valid
