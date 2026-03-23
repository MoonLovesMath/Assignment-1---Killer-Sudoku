"""
Board size: n^2, each box is a square of size n

Implement 3 main factor for a Killer Sudoku grid: Cell, Cage, Grid
"""

import math

class Cell:
    """
    The starting building block of a Sudoku grid
    
    Attributes:
        row, col    : 0-indexed row/col position
        value       : 0 if empty, 1..N otherwise
        cage_id     : which cage this cell belongs to (-1 until assigned)
    """

    def __init__(self, row: int, col: int):
        self.row            = row
        self.col            = col
        self.value: int     = 0
        self.cage_id: int   = 0

    def is_empty(self) -> bool:
        return self.value == 0

    def __repr__(self) -> str:
        v = self.value if self.value != 0 else "."
        return f"Cell({self.row},{self.col})={v}"  


class Cage:
    """
    A cage containing many cells, with a given sum
    No number appears more than once in a cage

    Attributes:
        cage_id     : unique identifier
        target      : required sum of all cell values
        cells       : list of Cell objects inside this cage
    """

    def __init__(self, cage_id: int, target: int, cells: list[Cell]):
        self.cage_id    = cage_id
        self.target     = target
        self.cells      = cells
        for cell in cells:
            cell.cage_id = cage_id

    @property
    def size(self) -> int:
        return len(self.cells)
    
    @property
    def current_sum(self) -> int:
        return sum(c.value for c in self.cells if not c.is_empty())
    
    @property
    def is_complete(self) -> bool:
        return all(not c.is_empty() for c in self.cells)
    
    @property
    def is_valid(self) -> bool:
        """Is the cage valid, up until now?"""
        filled = [c.value for c in self.cells if not c.is_empty()]
        if len(filled) != len(set(filled)):
            return False
        if self.is_complete:
            return self.current_sum == self.target
        return self.current_sum <= self.target
    
    def __repr__(self) -> str:
        coords = [(c.row, c.col) for c in self.cells]
        return f"Cage(id={self.cage_id}, target={self.target}, cells={coords})"
    

class Grid:
    """ 
    A N x N grid representing the game board
    N must be a perfect square (4, 9, 16, ...)

    Attributes:
        n           : board dimension
        box_size    : sub-box dimension = sqrt(n)
        cages:      : list of all Cage objects
        cells       : 2D list of Cell objects [row][col]
    """

    def __init__(self, n: int, cages: list[Cage]):
        assert math.isqrt(n) ** 2 == n, f"N must be a perfect square, but {n} is not"

        self.n          = n
        self.box_size   = math.isqrt(n)
        self.cages      = cages

        # 2D cell array
        self.cells: list[list[Cell]] = [
            [Cell(r, c) for c in range(n)] for r in range(n)
        ] 

        # Link cage cells to this grid's cells
        for cage in self.cages:
            cage.cells = [self.cells[cell.row][cell.col] for cell in cage.cells]
            for cell in cage.cells:
                cell.cage_id = cage.cage_id

        # O(1) cage lookup by position
        self.cell_to_cage = {}
        for cage in self.cages:
            for cell in cage.cells:
                key = (cell.row, cell.col)
                self.cell_to_cage[key] = cage


    # ------------ Accessors ------------
    def get_cell(self, row: int, col: int) -> Cell:
        return self.cells[row][col]
    
    def get_cage(self, row: int, col: int) -> Cage:
        return self.cell_to_cage[(row, col)]
    
    def row_peers(self, row: int) -> list[Cell]:
        return self.cells[row]
    
    def col_peers(self, col: int) -> list[Cell]:
        return [self.cells[r][col] for r in range(self.n)]
    
    def box_peers(self, row: int, col: int) -> list[Cell]:
        br = (row // self.box_size) * self.box_size
        bc = (col // self.box_size) * self.box_size

        return [
            self.cells[br + dr][bc + dc]
            for dr in range(self.box_size)
            for dc in range(self.box_size)
        ]

    def all_peers(self, row: int, col: int) -> set[Cell]:
        """All cells sharing a col, a row, or a box, excluding itself"""
        cell    = self.cells[row][col]
        peers   = set(self.row_peers(row)) | set(self.col_peers(col)) | set(self.box_peers(row, col))

        peers.discard(cell)
        return peers
    

    # ------------ State ------------
    def is_solved(self) -> bool:
        all_filled = all(not self.cells[r][c].is_empty() for r in range(self.n) for c in range(self.n))
        return all_filled and all(cage.is_valid for cage in self.cages)
    
    def reset(self):
        """Clear the board"""
        for r in range(self.n):
            for c in range(self.n):
                self.cells[r][c].value = 0


    # ------------ Display ------------
    def __str__(self) -> str:
        lines = []
        for r in range(self.n):
            row_str = " ".join(
                str(self.cells[r][c].value) if not self.cells[r][c].is_empty() else "."
                for c in range(self.n)
            )
            lines.append(row_str)
            if (r + 1) % self.box_size == 0 and r + 1 < self.n:
                lines.append("-" * (self.n * 2 - 1))
        return "\n".join(lines)

    def __repr__(self) -> str:
        return f"Grid(n={self.n}, cages={len(self.cages)})"  

        
