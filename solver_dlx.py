"""
Solver using Algorithm X + Dancing Links technique(DLX)

Strongly recommend you look this algo up before reading the code

Algorithm X (le GOAT - Knuth, 2000):
    An exact cover solver - given a 0/1 matrix, find a set of rows such that
    every column contains exactly one 1. Killer Sudoku is reduced to this problem.

Dancing Links:
    Is a data structure + implementation trick to make algorithm X faster
    Represent matrix as circular doubly linked list

Reduction: Killer Sudoku -> Exact Cover (taking example for N = 9)
    1. Cell: One cell could only have one digit      R1C1 = {R1C1#1, R1C1#2, ... , R1C1#9}       -> N^2 constraints
    2. Row: One row could have only one 'x' digit    R1#1 = {R1C1#1, R1C2#1, ... , R1C9#1}       -> N^2 constraints
    3. Col: One col could have only one 'x' digit    C1#1 = {R1C1#1, R2C1#1, ... , R9C1#1}       -> N^2 constraints
    4. Box: One box could have only one 'x' digit    B1#1 = {R1C1#1, R1C2#1, ... , R3C3#1}       -> N^2 constraints

    Matrix: N^3 x (4N^2)
"""

from models import Grid
from itertools import combinations


# ---------- Implement Dancing Links ----------
class _Node:
    """A single Node in the Dancing Links matrix"""

    __slots__ = ("left", "right", "up", "down", "col", "row_id", "size", "name")

    def __init__(self, name: str = ""):
        self.left:   "_Node" = self
        self.right:  "_Node" = self
        self.up:     "_Node" = self
        self.down:   "_Node" = self
        self.col:    "_Node" = self     # column header (headers point to themselves)
        self.row_id: int     = -1
        self.size:   int     = 0        # only meaningful on column headers
        self.name:   str     = name     # only meaningful on column headers


class _DLX:
    """
    The full Dancing Links matrix — circular doubly linked list of 1-nodes.

    The funny thing is that DLX never has a 0 in it. It's all 1s.
    Every node represents a 1 in the 0/1 matrix, pointing to the nearest 1.
    Let that sink in.
    """

    def __init__(self, num_cols: int, col_names: list[str]):
        # Root: dummy entry node, not a real column header
        self.root = _Node("root")

        # Build column headers as circular doubly-linked list
        self.cols: list[_Node] = []
        prev = self.root
        for name in col_names:
            col        = _Node(name)
            col.col    = col        # header points to itself
            col.left   = prev
            prev.right = col
            prev       = col
            self.cols.append(col)
        prev.right     = self.root
        self.root.left = prev

    def add_row(self, row_id: int, col_indices: list[int]):
        """Insert one row into the matrix without disturbing column headers."""
        if not col_indices:
            return

        nodes: list[_Node] = []
        for ci in col_indices:
            col         = self.cols[ci]
            node        = _Node()
            node.col    = col
            node.row_id = row_id

            # Attach vertically (insert above column header = end of column)
            node.up     = col.up
            node.down   = col
            col.up.down = node
            col.up      = node
            col.size   += 1

            nodes.append(node)

        # Link horizontally into a circular list
        for i, node in enumerate(nodes):
            node.right = nodes[(i + 1) % len(nodes)]
            node.left  = nodes[(i - 1) % len(nodes)]

    # ------------ Cover / Uncover ------------

    def _cover(self, col: _Node):
        """Unlink col header and every row that touches it."""
        col.right.left = col.left
        col.left.right = col.right
        row = col.down
        while row is not col:
            node = row.right
            while node is not row:
                node.down.up   = node.up
                node.up.down   = node.down
                node.col.size -= 1
                node           = node.right
            row = row.down

    def _uncover(self, col: _Node):
        """Relink col header and every row that touches it (exact reverse of cover)."""
        row = col.up
        while row is not col:
            node = row.left
            while node is not row:
                node.col.size += 1
                node.down.up   = node
                node.up.down   = node
                node           = node.left
            row = row.up
        col.right.left = col
        col.left.right = col
    # Link/Unlink (per node) is O(1)

    # ------------ Algorithm X ------------

    def search(self, solution: list[int], cage_check=None) -> bool:
        """
        Recursive Algorithm X.
        Returns True if a valid solution is found, False otherwise.

        cage_check: optional callable(solution) -> bool
            Called when all columns are covered to verify cage sums.
            If it returns False, this "solution" is rejected and we backtrack.
        """

        # Logically, I could (fundamentally) understand the clever idea of
        # this algorithm. But if you ask me how THIS specific implementation
        # works? Yeah, I would rather shoot myself in the leg.

        if self.root.right is self.root:
            # All columns covered — but we still need to verify cage sums
            if cage_check and not cage_check(solution):
                return False
            return True

        # Choose column with fewest nodes (S-heuristic, minimises branching)
        col = self._choose_col()

        self._cover(col)
        row = col.down
        while row is not col:
            solution.append(row.row_id)

            node = row.right
            while node is not row:
                self._cover(node.col)
                node = node.right

            if self.search(solution, cage_check):
                return True

            # Backtrack
            solution.pop()
            node = row.left
            while node is not row:
                self._uncover(node.col)
                node = node.left

            row = row.down

        self._uncover(col)
        return False

    def _choose_col(self) -> _Node:
        """S-heuristic: column with the fewest live nodes minimises branching."""
        best = self.root.right
        node = best.right
        while node is not self.root:
            if node.size < best.size:
                best = node
            node = node.right
        return best


# ---------- Killer Sudoku -> Exact Cover Reduction ----------

def _build_dlx(grid: Grid) -> tuple[_DLX, list[tuple[int, int, int]], object]:
    n  = grid.n
    bs = grid.box_size

    # Valid digit sets and combo sets per cage
    # valid_digits: digits that appear in at least one valid combo (for pre-filtering)
    # valid_combos: the actual valid frozensets (for base-case cage check)
    cage_valid_digits: dict[int, set[int]]        = {}
    cage_valid_combos: dict[int, list[frozenset]]  = {}

    for cage in grid.cages:
        combos = [
            combo for combo in combinations(range(1, n + 1), cage.size)
            if sum(combo) == cage.target
        ]
        cage_valid_digits[cage.cage_id] = {d for combo in combos for d in combo}
        cage_valid_combos[cage.cage_id] = [frozenset(combo) for combo in combos]

    # Column offsets
    base_cell = 0
    base_row  = n * n
    base_col  = n * n * 2
    base_box  = n * n * 3
    total     = n * n * 4

    col_names: list[str] = (
        [f"cell({r},{c})" for r in range(n) for c in range(n)]
      + [f"row({r}#{d})"  for r in range(n) for d in range(1, n + 1)]
      + [f"col({c}#{d})"  for c in range(n) for d in range(1, n + 1)]
      + [f"box({b}#{d})"  for b in range(n) for d in range(1, n + 1)]
    )

    dlx     = _DLX(total, col_names)
    row_map: list[tuple[int, int, int]] = []

    for r in range(n):
        for c in range(n):
            cage = grid.get_cage(r, c)
            box  = (r // bs) * bs + (c // bs)
            for d in sorted(cage_valid_digits[cage.cage_id]):
                row_id = len(row_map)
                row_map.append((r, c, d))
                dlx.add_row(row_id, [
                    base_cell + r * n + c,
                    base_row  + r * n + (d - 1),
                    base_col  + c * n + (d - 1),
                    base_box  + box * n + (d - 1),
                ])

    # Build cell->cage lookup for the cage_check closure
    cell_cage = [[grid.get_cage(r, c).cage_id for c in range(n)] for r in range(n)]

    def cage_check(solution: list[int]) -> bool:
        """Verify every cage's placed digits form a valid combination."""
        cage_digits: dict[int, set[int]] = {cage.cage_id: set() for cage in grid.cages}
        for row_id in solution:
            r, c, d = row_map[row_id]
            cage_digits[cell_cage[r][c]].add(d)
        return all(
            frozenset(cage_digits[cage.cage_id]) in cage_valid_combos[cage.cage_id]
            for cage in grid.cages
        )

    return dlx, row_map, cage_check


# ------------ Public solve ------------

def solve(grid: Grid) -> bool:
    dlx, row_map, cage_check = _build_dlx(grid)

    solution: list[int] = []
    if not dlx.search(solution, cage_check):
        return False

    for row_id in solution:
        r, c, d = row_map[row_id]
        grid.cells[r][c].value = d

    return True