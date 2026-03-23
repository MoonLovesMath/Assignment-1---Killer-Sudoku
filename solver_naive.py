"""
Naive solver - using pure backtracking

Solved from left to right, top to bottom. Possible digits (from 1..N) are tried in order
"""

from models import Cell, Grid


# Public solve API
def solve(grid: Grid) -> bool:
    return _backtrack(grid)


def _backtrack(grid: Grid) -> bool:
    """Core backtracking algorithm"""
    cell = _next_empty(grid)

    if cell is None:
        return True
    
    for digit in range(1, grid.n + 1):
        cell.value = digit

        if _is_consistent(grid, cell):
            if _backtrack(grid):
                return True
        
        cell.value = 0      # Backtrack

    return False


def _next_empty(grid: Grid) -> Cell | None:
    """Returns the first empty cell scanned"""
    for r in range(grid.n):
        for c in range(grid.n):
            if grid.cells[r][c].is_empty():
                return grid.cells[r][c]
    return None


# ------------ Constraints checking ------------
def _is_consistent(grid: Grid, cell: Cell) -> bool:
    """For the given cell, check if the grid is 'consistent' """
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