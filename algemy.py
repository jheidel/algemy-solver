from __future__ import print_function
from ortools.constraint_solver import pywrapcp
import time


# TODO: move board definitions to interface + class
# TODO: implement hexagonal board variants


def validate_board_rect(board, colors):
  if not board:
    raise ValueError('Board has no rows')

  height = len(board) 
  width = max(len(r) for r in board)
  if not width:
    raise ValueError('Board has no columns')

  if not all(len(r) == width for r in board):
    raise ValueError('Columns must all be the same size')

  for r in board:
    for c in r:
      if c.strip() != '' and c not in colors:
        raise ValueError('Unknown crystal color \'%s\'' % c)


def get_dimensions_board_rect(grid):
    rows = max(r for r, _ in list(grid.keys())) + 1
    cols = max(c for _, c in list(grid.keys())) + 1
    return rows, cols


def find_board_sightlines_rect(grid):
    """Yields lists for each sightline on the board."""
    rows, cols = get_dimensions_board_rect(grid)

    # TODO: refactor this to avoid duplication. Maybe make it common so it can
    # be re-used for hexagonal case.
   
    for r in range(rows):
        acc = []
        for c in range(cols):
            el = grid[(r, c)]
            if el:
                acc.append(el)
            else:
                if len(acc) > 1:
                    yield list(acc)
                acc[:] = []
        if len(acc) > 1:
            yield list(acc)

    for c in range(cols):
        acc = []
        for r in range(rows):
            el = grid[(r, c)]
            if el:
                acc.append(el)
            else:
                if len(acc) > 1:
                    yield list(acc)
                acc[:] = []
        if len(acc) > 1:
            yield list(acc)


def find_point_sightlines_rect(grid, r, c):
    """Yields all points that are visible from a given point."""
    rows, cols = get_dimensions_board_rect(grid)

    # TODO: refactor this to avoid duplication. Maybe make it common so it can
    # be re-used for hexagonal case.

    # Top
    for x in range(r, 0, -1):
        el = grid[(x - 1, c)]
        if el:
            yield el
        else:
            break
    # Bottom
    for x in range(r, rows - 1):
        el = grid[(x + 1, c)]
        if el:
            yield el
        else:
            break
    # Left
    for x in range(c, 0, -1):
        el = grid[(r, x - 1)]
        if el:
            yield el
        else:
            break
    # Right
    for x in range(c, cols - 1):
        el = grid[(r, x + 1)]
        if el:
            yield el
        else:
            break


def main():
  # Define all possible input colors.
  input_colors = ['R', 'B', 'Y']

  # Define all possible crystal colors.
  board_colors = ['R', 'B', 'Y']

  # Define how input colors can mix to crystal colors.
  mixings = {}  # TODO

  # Defines the initial state of the game board (the position of the crystals).
  board = [[' ', 'Y', ' ', ' ', ' '],
           [' ', ' ', ' ', ' ', ' '],
           ['R', ' ', ' ', ' ', 'R'],
           [' ', ' ', ' ', ' ', ' '],
           [' ', ' ', ' ', 'Y', ' ']]

  # -- End adjustable parameters --

  try:
    validate_board_rect(board, board_colors)
  except ValueError as err:
    print('Board validation failed: %s' % err)
    return

  # Create the solver.
  solver = pywrapcp.Solver('algemy')

  start = time.time()

  grid = {}
  for r, row in enumerate(board):
    for c, el in enumerate(row):
      if el in board_colors:
        grid[(r, c)] = None  # crystal position
      else:
        grid[(r, c)] = solver.IntVar(0, len(input_colors), '<r%i,c%i>' % (r, c))

  # TODO: CONSTRAINT - crystal illumination

  # TODO: CONSTRAINT - board sightlines
  sightlines = list(find_board_sightlines_rect(grid))
  print("Board sightlines: %s\n\n" % sightlines)

  # TODO: CONSTRAINT - all points solved
  test = list(find_point_sightlines_rect(grid, 4, 3))
  print("Point sightlines: %s\n\n" % test)


  print("Grid %s\n\n" % grid)
  all_vars = list(filter(None, grid.values()))

  vars_phase = solver.Phase(all_vars,
                            solver.INT_VAR_DEFAULT,
                            solver.INT_VALUE_DEFAULT)

  print("Time setting up constraints: %.2fms" % ((time.time() - start) * 1000))

  # TODO: solve and print solution


if __name__ == '__main__':
  main()
