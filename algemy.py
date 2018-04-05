from __future__ import print_function
from ortools.constraint_solver import pywrapcp
import time
import re

from board import RectBoard
from board import HexBoard

# 
# Defines a solver for the game of Algemy.
#
# See line 219 for configuring a board to solve.
#


def validate_colors(board, input_colors, mixing_rules):
  def get_board_colors():
    for row in board:
      for el in row:
        if el.strip() != '':
          yield el
  board_colors = set(get_board_colors())

  for c in board_colors:
    if c not in mixing_rules:
      raise ValueError('Missing mixing rule for board color \'%s\'' % c)

  for k, v in mixing_rules.items():
    if not v:
      raise ValueError('Empty rules for board color \'%s\'' % k)
    for rule in v:
      if not rule:
        raise ValueError('Empty rule in set for board color \'%s\'' % k)
      for s in rule:
        if s[0] not in ('+', '-'):
          raise ValueError('Invalid format for mixing rule \'%s\'' % s)
        if s[1:] not in input_colors:
          raise ValueError('Mixing rule \'%s\' did not match an input color' % s)


# Color key:
#  - R: Red
#  - O: Orange
#  - Y: Yellow
#  - G: Green
#  - B: Blue
#  - V: Violet/Pink/Purple
#  - W: White (unset)
#  - X: Brown (combination of multiple colors)

##
## Define all possible input colors.
##

EASY_INPUT_COLORS = ['R', 'Y', 'B']

HARD_INPUT_COLORS = ['R', 'O', 'Y', 'G', 'B', 'V']

## 
## Define mapping of crystals to input colors.
## 
# 
# Mixings `key` is the crystal colors, The `value` is a set of rule
# definitions. for example, the following rule
#
#   'O': [('+R', '+Y', '-B'), ('+O', '-G', '-B', '-V')],
#
# Maps to this logical statement:
# 
#   An ORANGE crystal is satisfied when:
#     (There exists a RED and YELLOW source in its sight-lines,
#      but no BLUE)
#     OR
#     (There exists an ORANGE crystal in its sight-lines,
#      but no GREEN, BLUE, or VIOLET)
#     

EASY_MIXING_RULES = {
  'R': [('+R', '-Y', '-B')],
  'O': [('+R', '+Y', '-B')],
  'Y': [('-R', '+Y', '-B')],
  'G': [('-R', '+Y', '+B')],
  'B': [('-R', '-Y', '+B')],
  'V': [('+R', '-Y', '+B')],
  'W': [('-R', '-Y', '-B')],
  'X': [('+R', '+Y', '+B')],
}

HARD_MIXING_RULES = {
  'R': [('+R', '-O', '-Y', '-G', '-B', '-V')],
  'O': [('+R', '+Y', '-G', '-B', '-V'), ('+O', '-G', '-B', '-V')],
  'Y': [('-R', '-O', '+Y', '-G', '-B', '-V')],
  'G': [('-R', '-O', '+Y', '+B', '-V'), ('+G', '-V', '-R', '-O')],
  'B': [('-R', '-O', '-Y', '-G', '+B', '-V')],
  'V': [('+R', '-O', '-Y', '-G', '+B'), ('+V', '-O', '-Y', '-G')],
  'W': [('-R', '-O', '-Y', '-G', '-B', '-V')],
  'X': [('+R', '+Y', '+B'),
        ('+R', '+G'), ('+O', '+B'), ('+Y', '+V'),
        ('+O', '+G'), ('+G', '+V'), ('+V', '+O')],
}


def solve_board(board, expanded_colors, verbose=False):

  # Identify the input colors and mixing rules used based on the level.
  input_colors = HARD_INPUT_COLORS if expanded_colors else EASY_INPUT_COLORS
  mixing_rules = HARD_MIXING_RULES if expanded_colors else EASY_MIXING_RULES

  try:
    if RectBoard.is_rect_board(board):
      RectBoard.validate(board)
    else:
      HexBoard.validate(board)
    validate_colors(board, input_colors, mixing_rules)
  except ValueError as err:
    print('Board validation failed: %s' % err)
    return

  # Create the solver.
  solver = pywrapcp.Solver('algemy')

  start = time.time()

  grid = {}
  for r, row in enumerate(board):
    for c, el in enumerate(row):
      if el.strip() == '':
        # A solvable position.
        grid[(r, c)] = solver.IntVar(0, len(input_colors), '<Row %i, Col %i>' % (r, c))
      else:
        grid[(r, c)] = None  # crystal position

  if RectBoard.is_rect_board(board):
    b = RectBoard(grid)
  else:
    b = HexBoard(grid)

  # Helper: converts an input color to the int var space.
  color_i = lambda c: input_colors.index(c) + 1
  # Helper: converts an int var to the input color string.
  i_color = lambda i: input_colors[i - 1]

  # CONSTRAINT - crystal illumination
  for (r, c), el in grid.items():
    if el is not None:
      continue  # only look at crystals
    sight_points = list(b.find_point_sightlines(r, c))

    or_rules = []
    for mix_rule in mixing_rules[board[r][c]]:
      pos_colors = [s[1:] for s in mix_rule if s[0] == '+']
      def get_pos_rules():
        for color in pos_colors:
          yield solver.Sum(p == color_i(color) for p in sight_points) >= 1

      neg_colors = [s[1:] for s in mix_rule if s[0] == '-']
      def get_neg_rules():
        for color in neg_colors:
          yield solver.Sum(p == color_i(color) for p in sight_points) == 0

      comb_rules = list(get_pos_rules()) + list(get_neg_rules())
      final_rule = solver.Sum(comb_rules) == len(comb_rules) # ALL
      or_rules.append(final_rule)

    solver.Add(solver.Sum(or_rules) > 0) # ANY

  # CONSTRAINT - board sightlines
  for sightline in b.find_board_sightlines():
    # At one item can be set (non-zero) in a sightline.
    solver.Add(solver.Sum(x > 0 for x in sightline) <= 1)

  # CONSTRAINT - all points solved
  for (r, c), el in grid.items():
    if el is None:
      continue  # ignore crystals
    # Either the point is non-empty or a point in its sightline is non-empty.
    solver.Add(el + solver.Sum(b.find_point_sightlines(r, c)) > 0)

  all_vars = list(filter(None, grid.values()))
  vars_phase = solver.Phase(all_vars,
                            solver.INT_VAR_DEFAULT,
                            solver.INT_VALUE_DEFAULT)

  if verbose:
    print("Time setting up constraints: %.2fms" % ((time.time() - start) * 1000))

  solution = solver.Assignment()
  solution.Add(all_vars)
  collector = solver.FirstSolutionCollector(solution)
  start = time.time()
  solver.Solve(vars_phase, [collector])

  if verbose:
    print("Solve time: %.2fms" % (1000 * (time.time() - start)))

  if collector.SolutionCount() < 1:
    print("\nNO SOLUTION FOUND")
    return None

  # TODO iterate over all solutions instead of using collector.
  # Allow finding first one then prompt to find next or maybe all.

  def lookup(r, c):
    el = grid[(r, c)]
    if el is None:
      return ' '
    s = int(collector.Value(0, el))
    if not s:
      return ' '
    return i_color(s)

  solution = []
  for r, row in enumerate(board):
    solution.append([lookup(r, c) for c in range(len(row))])
  return solution


def main():
  # -- BEGIN ADJUSTABLE PARAMETERS --

  # Whether the user is allowed to input the expanded color set.
  # The first two rows of the game use the basic color set.
  # The third row allows use of the expanded set.
  expanded_colors = False

  # Defines the initial state of the game board (the position of the crystals).
  # See the color key above for valid inputs.
  board = [[' ', ' ', ' '],
           ['R', 'R', ' ', ' '],
           ['B', ' ', ' ', ' ', ' '],
           ['Y', 'Y', ' ', ' '],
           [' ', ' ', ' ']] 

  # -- END ADJUSTABLE PARAMETERS --

  print("INPUT BOARD")
  for r in board:
    print(' '.join((c if c.strip() != '' else '-') for c in r))
  print()

  solution = solve_board(board, expanded_colors, verbose=True)
  if solution is None:
    return

  print("\nFOUND SOLUTION")

  # Render solution graphically.
  for row in solution:
    print(' '.join(el.replace(' ','-') for el in row))


if __name__ == '__main__':
  main()
