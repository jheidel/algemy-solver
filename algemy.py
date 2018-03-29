from __future__ import print_function
from ortools.constraint_solver import pywrapcp
import time


def validate_board(board, colors):
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

  return (width, height)
  

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
           [' ', ' ', ' ', ' ', ' '],
           [' ', ' ', ' ', 'Y', ' ']]

  # -- End adjustable parameters --

  try:
    board_width, board_height = validate_board(board, board_colors)
  except ValueError as err:
    print('Board validation failed: %s' % err)
    return

  # Create the solver.
  solver = pywrapcp.Solver('algemy')

  grid = {}
  for i in range(board_width):
    for j in range(board_height):
      if board[j][i] in board_colors:
        grid[(i, j)] = None  # Crystal position
      else:
        grid[(i, j)] = solver.IntVar(0, len(input_colors), '<x%i,y%i>' % (i, j))

  # TODO: add all constraints

  all_vars = list(filter(None, grid.values()))

  # TODO: remove debug
  print(all_vars)

  vars_phase = solver.Phase(all_vars,
                            solver.INT_VAR_DEFAULT,
                            solver.INT_VALUE_DEFAULT)

  # TODO: solve and print solution


if __name__ == '__main__':
  main()
