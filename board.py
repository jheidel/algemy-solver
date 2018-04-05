
def to_board_sightlines(point_lists):
  for l in point_lists:
    acc = []
    for el in l:
      if el:
        acc.append(el)
      else:
        if len(acc) > 1:
          yield list(acc)
        acc[:] = []
    if len(acc) > 1:
      yield list(acc)


class RectBoard:

  @staticmethod
  def is_rect_board(board):
    mr = max(len(r) for r in board)
    return all(len(r) == mr for r in board)

  @staticmethod
  def validate(board):
    if not board:
      raise ValueError('Board has no rows')

    height = len(board) 
    width = max(len(r) for r in board)
    if not width:
      raise ValueError('Board has no columns')
    
    if not all(len(r) == width for r in board):
      raise ValueError('Columns must all be the same size')

  def __init__(self, grid):
    self.grid = grid

  def get_dimensions(self):
      rows = max(r for r, _ in list(self.grid.keys())) + 1
      cols = max(c for _, c in list(self.grid.keys())) + 1
      return rows, cols

  def find_board_sightlines(self):
    """Yields a list of points for each sightline on the board."""
    rows, cols = self.get_dimensions()

    for s in to_board_sightlines([[self.grid[(r, c)] for r in range(rows)] for c in range(cols)]):
        yield s
    for s in to_board_sightlines([[self.grid[(r, c)] for c in range(cols)] for r in range(rows)]):
        yield s

  def point_iterator(self, r, c, dr, dc):
    while True:
      r += dr
      c += dc
      if (r, c) not in self.grid:
        break
      el = self.grid[(r, c)]
      if el:
        yield el
      else:
        break

  def find_point_sightlines(self, r, c):
    """Yields all points that are visible from a given point."""
    for p in self.point_iterator(r, c, -1, 0):
      yield p
    for p in self.point_iterator(r, c, 1, 0):
      yield p
    for p in self.point_iterator(r, c, 0, -1):
      yield p
    for p in self.point_iterator(r, c, 0, 1):
      yield p


# Helpful reading for cube coordinate representation of a hexagonal grid.
# https://www.redblobgames.com/grids/hexagons/
class HexBoard:

  @staticmethod
  def validate(board):
    if not board:
      raise ValueError('Board has no rows')

    width = max(len(r) for r in board)
    if not width:
      raise ValueError('Board has no columns')

    row_max = max(enumerate(board), key=lambda k: len(k[1]))[0]
    for i, row in enumerate(board):
      if len(row) != width - abs(i - row_max):
        raise ValueError('Board rows not hexagonal')

  def __init__(self, grid):
    self.grid = grid
    self.cube_grid = {}
    for (r, c), v in grid.items():
      self.cube_grid[self.rc2cube(r, c)] = v

  def rc2cube(self, r, c):
    row_max = max(self.grid.keys(), key=lambda k: k[1])[0]
    z = r
    if r <= row_max:
      y = -1 * c
    else:
      y = -c - (r - row_max)
    x = -y - z
    return (x, y, z)

  def board_iterator(self, x, y, z, dx, dy, dz):
    while (x, y, z) in self.cube_grid:
      yield self.cube_grid[(x, y, z)]
      x += dx
      y += dy
      z += dz

  def find_board_sightlines(self):
    """Yields a list of points for each sightline on the board."""
    def grid_iter():
      x = min(p[0] for p in self.cube_grid.keys())
      while any(k[0] == x for k in self.cube_grid.keys()):
        y = min(k[1] for k in self.cube_grid.keys() if k[0] == x)
        z = -x-y
        yield list(self.board_iterator(x, y, z, 0, 1, -1))
        x += 1

      y = min(p[1] for p in self.cube_grid.keys())
      while any(k[1] == y for k in self.cube_grid.keys()):
        x = min(k[0] for k in self.cube_grid.keys() if k[1] == y)
        z = -x-y
        yield list(self.board_iterator(x, y, z, 1, 0, -1))
        y += 1

      z = min(p[2] for p in self.cube_grid.keys())
      while any(k[2] == z for k in self.cube_grid.keys()):
        x = min(k[0] for k in self.cube_grid.keys() if k[2] == z)
        y = -x-z
        yield list(self.board_iterator(x, y, z, 1, -1, 0))
        z += 1

    for s in to_board_sightlines(grid_iter()):
        yield s

  def point_iterator(self, x, y, z, dx, dy, dz):
    while True:
      x += dx
      y += dy
      z += dz
      if (x, y, z) not in self.cube_grid:
        break
      el = self.cube_grid[(x, y, z)]
      if el:
        yield el
      else:
        break

  def find_point_sightlines(self, r, c):
    """Yields all points that are visible from a given point."""
    x, y, z = self.rc2cube(r, c)
    for p in self.point_iterator(x, y, z, 1, -1, 0):
      yield p
    for p in self.point_iterator(x, y, z, 1, 0, -1):
      yield p
    for p in self.point_iterator(x, y, z, 0, 1, -1):
      yield p
    for p in self.point_iterator(x, y, z, -1, 1, 0):
      yield p
    for p in self.point_iterator(x, y, z, -1, 0, 1):
      yield p
    for p in self.point_iterator(x, y, z, 0, -1, 1):
      yield p
