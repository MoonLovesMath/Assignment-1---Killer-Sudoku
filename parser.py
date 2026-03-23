"""
Parses raw input data into a Grid object

Expected format:
    input_data = [
        (target, [(row, col), (row, col), ...]),
        ...
    ]
"""

import math
from models import Cell, Cage, Grid


def parse(input_data: list[tuple[int, list[tuple[int, int]]]]) -> Grid:
    """Convert raw input_data into a Grid"""
    n = _infer_n(input_data)
    _validate(input_data, n)

    cages = [
        Cage(cage_id=i, target=target, cells=[Cell(r, c) for r, c in coords])
        for i, (target, coords) in enumerate(input_data)
    ]

    return Grid(n, cages)


# ------------ Helpers ------------
def _infer_n(input_data: list) -> int:
    """Infer Grid's dimension N"""
    max_coords = max(
        max(r, c)
        for _, coords in input_data
        for r, c in coords
    )

    raw_n = max_coords + 1

    # Rounds up to nearest perfect square
    box_size = math.isqrt(raw_n)
    if box_size * box_size < raw_n:
        box_size += 1
    return box_size * box_size

def _validate(input_data: list, n: int):
    """Sanity check before building the grid"""

    seen: dict[tuple[int, int], int] = {}   # (row, col) -> cage_id

    for cage_id, (target, coords) in enumerate(input_data):

        # Target must be positive
        if target <= 0:
            raise ValueError(f"Cage {cage_id} has non-positive target: {target}")
        
        # Cage must not be empty
        if not coords:
            raise ValueError(f"Cage {cage_id} has no cells")
        
        for r, c in coords:

            # Coordinates must be in bounds:
            if not (0 <= r < n and 0 <= c < n):
                raise ValueError(f"Cage {cage_id}: coordinate ({r}, {c}) is out of bounds for {n}x{n} grid")
            
            # No cell can belong in two cages
            if (r, c) in seen:
                raise ValueError(f"Cell ({r}, {c}) is assigned to both cage {seen[(r, c)]} and cage {cage_id}")
            
            seen[(r, c)] = cage_id

    # Every cell in the grid must be covered
    missing = [
        (r, c)
        for r in range(n)
        for c in range(n)
        if (r, c) not in seen
    ]

    if missing:
        raise ValueError(f"{len(missing)} cell(s) not covered by any cage: {missing}")
    