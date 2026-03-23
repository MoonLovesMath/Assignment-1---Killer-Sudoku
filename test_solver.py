"""
test_solvers.py — Verify all solvers produce correct solutions.

Test cases:
    4x4   — artificial puzzle, known unique solution, exact check
    9x9   — real generated puzzle (40 cages, sizes 1–3), validity check
    16x16 — real puzzle #1622, grid structure verified (not solved —
             neither backtracker nor DLX are fast enough on real 16x16 cages)
"""

import sys, os
sys.path.insert(0, os.path.dirname(__file__))

from parser import parse
import solver_naive
import solver_backtrack
import solver_dlx


# ─────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────

def make_puzzle(solution, cage_cells):
    return [
        (sum(solution[r][c] for r, c in cells), cells)
        for cells in cage_cells
    ]


def assert_exact(grid, expected, label):
    assert grid.is_solved(), f"{label}: grid.is_solved() = False\n{grid}"
    for r in range(grid.n):
        for c in range(grid.n):
            got, exp = grid.cells[r][c].value, expected[r][c]
            assert got == exp, f"{label}: ({r},{c}) = {got}, expected {exp}\n{grid}"
    print(f"  ✓ correct")


def assert_valid(grid, label):
    assert grid.is_solved(), f"{label}: grid.is_solved() = False\n{grid}"
    print(f"  ✓ valid solution found")


def run_solver(label, input_data, solver, check, skip=False):
    print(f"\n{'─'*55}\n{label}\n{'─'*55}")
    if skip:
        print(f"  skipped")
        return "skip"
    grid   = parse(input_data)
    print(f"  {grid.n}x{grid.n}, {len(grid.cages)} cages")
    result = solver.solve(grid)
    assert result, f"{label}: solver returned False"
    check(grid, label)
    return "pass"


def run_parse_only(label, input_data):
    """Parse and validate grid structure — no solving."""
    print(f"\n{'─'*55}\n{label}\n{'─'*55}")
    grid = parse(input_data)
    n    = grid.n
    print(f"  {n}x{n}, {len(grid.cages)} cages")
    covered  = {(cell.row, cell.col) for cage in grid.cages for cell in cage.cells}
    expected = {(r, c) for r in range(n) for c in range(n)}
    assert covered == expected, f"cells mismatch — missing {expected - covered}"
    assert all(cage.size > 0 for cage in grid.cages), "empty cage found"
    print(f"  ✓ all {n*n} cells covered, all cages non-empty")
    return "pass"


# ─────────────────────────────────────────────
# 4x4 — unique artificial puzzle
# ─────────────────────────────────────────────

SOLUTION_4 = [
    [3, 4, 1, 2],
    [2, 1, 4, 3],
    [4, 3, 2, 1],
    [1, 2, 3, 4],
]
INPUT_4 = make_puzzle(SOLUTION_4, [
    [(0,0),(0,1)], [(0,2),(0,3)],
    [(1,0),(2,0)], [(1,1),(1,2)],
    [(1,3),(2,3)], [(2,1),(2,2)],
    [(3,0),(3,1)], [(3,2),(3,3)],
])


# ─────────────────────────────────────────────
# 9x9 — real generated puzzle (seed=42, easy)
# 40 cages, sizes 1–3, may be non-unique → validity check only
# ─────────────────────────────────────────────

INPUT_9 = [
    (9,  [(1,6),(1,7)]),        (5,  [(5,2),(6,2)]),
    (15, [(3,3),(3,2)]),        (14, [(0,1),(0,0)]),
    (7,  [(1,0),(1,1),(2,1)]),  (14, [(2,8),(1,8)]),
    (6,  [(8,4),(7,4)]),        (21, [(5,7),(4,7),(5,6)]),
    (9,  [(7,6),(7,7)]),        (11, [(0,3),(0,2)]),
    (6,  [(8,6),(8,7)]),        (8,  [(2,7),(3,7)]),
    (10, [(7,8),(6,8)]),        (15, [(3,5),(3,4)]),
    (16, [(3,1),(3,0),(4,1)]),  (4,  [(0,8),(0,7)]),
    (9,  [(5,4),(5,3)]),        (9,  [(4,5),(5,5),(6,5)]),
    (16, [(6,6),(6,7)]),        (14, [(7,5),(8,5)]),
    (12, [(8,0),(7,0)]),        (13, [(8,1),(7,1)]),
    (9,  [(2,3),(2,2)]),        (12, [(4,2),(4,3)]),
    (13, [(2,4),(2,5),(1,4)]),  (14, [(6,4),(6,3)]),
    (11, [(0,6),(0,5)]),        (11, [(7,2),(8,2),(7,3)]),
    (6,  [(6,1),(5,1)]),        (6,  [(1,5)]),
    (16, [(4,6),(3,6),(2,6)]),  (5,  [(0,4)]),
    (15, [(4,0),(5,0),(6,0)]),  (1,  [(4,4)]),
    (13, [(5,8),(4,8)]),        (7,  [(2,0)]),
    (11, [(1,3),(1,2)]),        (4,  [(8,8)]),
    (1,  [(3,8)]),              (7,  [(8,3)]),
]


# ─────────────────────────────────────────────
# 16x16 — real puzzle #1622
# 135 cages — parse and validate structure only, no solving
# ─────────────────────────────────────────────

INPUT_16 = [
    (22, [(0,0),(1,0)]),
    (25, [(0,1),(1,1)]),
    (26, [(0,2),(0,3),(1,3)]),
    (18, [(0,4),(1,4)]),
    (4,  [(0,5),(1,5)]),
    (24, [(0,6),(1,6)]),
    (18, [(0,7),(0,8)]),
    (38, [(0,9),(0,10),(1,9),(1,10)]),
    (17, [(0,11),(1,11)]),
    (21, [(0,12),(1,12)]),
    (14, [(0,13),(0,14),(0,15)]),
    (33, [(1,2),(2,1),(2,2)]),
    (13, [(1,7),(1,8)]),
    (21, [(1,13),(2,13)]),
    (17, [(1,14),(1,15)]),
    (15, [(2,0),(3,0)]),
    (9,  [(2,3),(2,4)]),
    (20, [(2,5),(3,5)]),
    (12, [(2,6),(2,7)]),
    (20, [(2,8),(3,8)]),
    (8,  [(2,9),(2,10)]),
    (16, [(2,11),(3,11)]),
    (8,  [(2,12)]),
    (19, [(2,14),(3,14)]),
    (11, [(2,15)]),
    (11, [(3,1),(4,1)]),
    (5,  [(3,2)]),
    (14, [(3,3),(4,3)]),
    (28, [(3,4),(4,4),(4,5)]),
    (21, [(3,6),(3,7)]),
    (21, [(3,9),(3,10)]),
    (12, [(3,12),(3,13)]),
    (13, [(3,15)]),
    (17, [(4,0),(5,0)]),
    (4,  [(4,2)]),
    (11, [(4,6)]),
    (20, [(4,7),(4,8)]),
    (20, [(4,9),(5,9)]),
    (17, [(4,10),(4,11)]),
    (34, [(4,12),(5,11),(5,12)]),
    (22, [(4,13),(5,13)]),
    (9,  [(4,14),(5,14)]),
    (10, [(4,15),(5,15),(6,15)]),
    (25, [(5,1),(6,1)]),
    (16, [(5,2),(6,2)]),
    (18, [(5,3),(5,4)]),
    (19, [(5,5),(6,5)]),
    (1,  [(5,6)]),
    (19, [(5,7),(6,7)]),
    (19, [(5,8),(6,8)]),
    (5,  [(5,10)]),
    (3,  [(6,0)]),
    (8,  [(6,3)]),
    (17, [(6,4),(7,4)]),
    (2,  [(6,6)]),
    (16, [(6,9)]),
    (16, [(6,10),(7,10)]),
    (12, [(6,11)]),
    (28, [(6,12),(7,12)]),
    (5,  [(6,13)]),
    (19, [(6,14),(7,14)]),
    (22, [(7,0),(7,1),(8,0)]),
    (27, [(7,2),(7,3)]),
    (19, [(7,5),(7,6)]),
    (33, [(7,7),(7,8),(8,7),(8,8)]),
    (11, [(7,9)]),
    (7,  [(7,11)]),
    (4,  [(7,13)]),
    (28, [(7,15),(8,14),(8,15)]),
    (7,  [(8,1),(9,1)]),
    (15, [(8,2)]),
    (14, [(8,3),(9,3)]),
    (9,  [(8,4)]),
    (23, [(8,5),(9,5)]),
    (13, [(8,6)]),
    (13, [(8,9),(8,10)]),
    (11, [(8,11),(9,11)]),
    (12, [(8,12),(8,13)]),
    (20, [(9,0),(10,0),(11,0)]),
    (13, [(9,2)]),
    (11, [(9,4)]),
    (12, [(9,6)]),
    (4,  [(9,7),(10,7)]),
    (10, [(9,8),(10,8)]),
    (5,  [(9,9)]),
    (17, [(9,10),(10,10)]),
    (6,  [(9,12)]),
    (28, [(9,13),(10,13)]),
    (18, [(9,14),(10,14)]),
    (14, [(9,15)]),
    (8,  [(10,1),(11,1)]),
    (17, [(10,2),(11,2)]),
    (42, [(10,3),(10,4),(11,3)]),
    (5,  [(10,5)]),
    (12, [(10,6),(11,6)]),
    (12, [(10,9)]),
    (26, [(10,11),(10,12)]),
    (15, [(10,15),(11,15)]),
    (8,  [(11,4),(11,5)]),
    (31, [(11,7),(11,8)]),
    (13, [(11,9)]),
    (26, [(11,10),(11,11),(12,11)]),
    (4,  [(11,12),(12,12)]),
    (1,  [(11,13)]),
    (23, [(11,14),(12,14)]),
    (5,  [(12,0)]),
    (26, [(12,1),(13,1)]),
    (6,  [(12,2),(12,3)]),
    (16, [(12,4),(13,4)]),
    (20, [(12,5),(12,6)]),
    (17, [(12,7),(13,7)]),
    (26, [(12,8),(12,9)]),
    (20, [(12,10),(13,10)]),
    (16, [(12,13)]),
    (18, [(12,15),(13,15)]),
    (13, [(13,0)]),
    (15, [(13,2),(14,2)]),
    (7,  [(13,3)]),
    (8,  [(13,5),(13,6)]),
    (15, [(13,8),(13,9)]),
    (14, [(13,11),(13,12)]),
    (27, [(13,13),(13,14),(14,13)]),
    (17, [(14,0),(14,1)]),
    (17, [(14,3),(15,3)]),
    (16, [(14,4),(15,4)]),
    (40, [(14,5),(14,6),(15,5),(15,6)]),
    (18, [(14,7),(14,8)]),
    (17, [(14,9),(15,9)]),
    (3,  [(14,10),(15,10)]),
    (21, [(14,11),(15,11)]),
    (18, [(14,12),(15,12),(15,13)]),
    (25, [(14,14),(15,14)]),
    (12, [(14,15),(15,15)]),
    (30, [(15,0),(15,1),(15,2)]),
    (18, [(15,7),(15,8)]),
]


# ─────────────────────────────────────────────
# Test suite
# ─────────────────────────────────────────────

def main():
    print("=" * 55)
    print("KILLER SUDOKU — SOLVER TESTS")
    print("=" * 55)

    def exact_4(grid, label): assert_exact(grid, SOLUTION_4, label)

    solver_tests = [
        # label                  input    solver            check        skip
        ("4x4   | naive",     INPUT_4, solver_naive,     exact_4,      False),
        ("4x4   | backtrack", INPUT_4, solver_backtrack, exact_4,      False),
        ("4x4   | dlx",       INPUT_4, solver_dlx,       exact_4,      False),
        ("9x9   | naive",     INPUT_9, solver_naive,     assert_valid, False),
        ("9x9   | backtrack", INPUT_9, solver_backtrack, assert_valid, False),
        ("9x9   | dlx",       INPUT_9, solver_dlx,       assert_valid, False),
    ]

    passed = failed = skipped = 0

    for label, input_data, solver, check, skip in solver_tests:
        print(f"\n{'─'*55}\n{label}\n{'─'*55}")
        if skip:
            print("  skipped")
            skipped += 1
            continue
        try:
            grid   = parse(input_data)
            print(f"  {grid.n}x{grid.n}, {len(grid.cages)} cages")
            result = solver.solve(grid)
            assert result, f"{label}: solver returned False"
            check(grid, label)
            passed += 1
        except AssertionError as e:
            print(f"  ✗ FAILED: {e}")
            failed += 1
        except Exception as e:
            print(f"  ✗ ERROR: {type(e).__name__}: {e}")
            failed += 1

    # 16x16 — parse and validate only
    try:
        result = run_parse_only("16x16 | parse only (puzzle #1622)", INPUT_16)
        passed += 1
    except AssertionError as e:
        print(f"  ✗ FAILED: {e}")
        failed += 1
    except Exception as e:
        print(f"  ✗ ERROR: {type(e).__name__}: {e}")
        failed += 1

    print(f"\n{'='*55}")
    print(f"Results: {passed} passed, {failed} failed, {skipped} skipped")
    print(f"{'='*55}")
    return failed == 0


if __name__ == "__main__":
    sys.exit(0 if main() else 1)