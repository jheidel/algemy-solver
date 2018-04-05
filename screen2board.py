from __future__ import print_function
import numpy as np
import cv2
import math
import algemy


# Fraction of the top of the screen taken up by the menu.
TOP_CROP_FRAC = 0.25

# Average colors for each board crystal.
COLOR_MAP = {
  ' ': (255, 255, 255),
  'R': (159, 159, 187),
  'O': (126, 158, 185),
  'Y': (155, 183, 183),
  'G': (127, 161, 127), 
  'B': (187, 168, 168),
  'V': (175, 127, 175),
  'W': (221, 221, 221),
  'X': (102, 122, 142),
}

# Possible colors for the color-wheel, clockwise.
COLORS = ['R', 'O', 'Y', 'G', 'B', 'V']

# Color wheel radius as a fraction of board spacing.
WHEEL_RF = 0.75


def closest_color(r, g, b):
  v = 255
  ret = ''
  for c, (r2, g2, b2) in COLOR_MAP.items():
    d = math.sqrt((r - r2)**2 + (g - g2)**2 + (b - b2)**2)
    if d < v:
      v = d
      ret = c
  return ret


def dist(p1, p2):
  x1, y1 = p1
  x2, y2 = p2
  return int(math.sqrt((x2 - x1)**2 + (y2 - y1)**2))

def main():
  # TODO: make args
  # ARGS
  img = cv2.imread('/tmp/screen.png')
  expanded_colors = True
  debug = False
  # END ARGS

  height, width = img.shape[:2]

  # Crop out the top menu bar.
  img = img[int(height * TOP_CROP_FRAC):height, 0:width]

  # Convert to black & white.
  imggray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
  _, thresh = cv2.threshold(imggray, 127, 255, 0)
  _, contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

  # Traverse the contour tree to extract the inside of the grid (level 2 contours)
  l2_contours = []
  def traverse(i, level):
    while i != -1:
      if level == 2:
        l2_contours.append(contours[i])
      i, prev, child, parent = hierarchy[0][i]
      if child != -1:
        traverse(child, level + 1)
  traverse(0, 0)

  # Find center points of each grid square.
  centers = []
  for c in l2_contours:
    (x, y), _ = cv2.minEnclosingCircle(c)
    centers.append((int(x), int(y)))

  # Determine the spacing of our grid.
  spacing = min(dist(centers[0], c) for c in centers[1:])

  # Generate a top-down, left-right sort and split into rows.
  rows = {}
  for x, y in centers:
    closest_row = None
    for ry in rows.keys():
      if abs(ry - y) < spacing / 2:
        closest_row = ry
    if closest_row:
      rows[closest_row].append((x, y))
    else:
      rows[y] = [(x, y)]
  rows = list(rows.items())
  rows.sort()  # Sort top-down.
  rows = [sorted(row) for _, row in rows]  # Sort left-right.

  board = []
  for row in rows:
    board_row = []
    for x, y in row:
      dilate = int(spacing / 4)
      sample = img[(y-dilate):(y+dilate), (x-dilate):(x+dilate)]

      # TODO: filter out black and white pixels for more color averaging that's
      # less dependent on sample size.
      avg_color = tuple(np.mean(sample, axis=(0,1)))
      color = closest_color(*avg_color)
      board_row.append(color)

    board.append(board_row)

  print("# DETECTED")
  for row in board:
    print('# ' + ' '.join(el.replace(' ','-') for el in row))
  print()

  solution = algemy.solve_board(board, expanded_colors)
  if not solution:
    print("# No solution.")
    return

  print("# SOLUTION")
  for row in solution:
    print('# ' + ' '.join(el.replace(' ','-') for el in row))
  print()

  for r, row in enumerate(solution):
    for c, color in enumerate(row):
      x = rows[r][c][0]
      y = rows[r][c][1]
      cv2.circle(img, (x, y), 2, (0, 255, 0), 2)

      if color.strip() == '':
        continue

      cv2.circle(img, (x, y), 2, (0, 0, 255), 3)
      cv2.putText(img, str(color), (x - 5, y - 10), cv2.FONT_HERSHEY_SIMPLEX,  1, (0, 0, 255), 2)

      # Compensate for top cropping.
      y += int(height * TOP_CROP_FRAC)

      # Tap on square to bring up color wheel.
      print("adb shell input tap %i %i" % (x, y))

      deg = (360 / len(COLORS)) * COLORS.index(color)
      xd = math.sin(math.radians(deg)) * WHEEL_RF * spacing
      yd = -1 * math.cos(math.radians(deg)) * WHEEL_RF * spacing

      # Tap on the correct color.
      print("adb shell input tap %i %i" % (x + xd, y + yd))

  # Show image processing debug.
  if debug:
    cv2.imshow('debug', img)
    cv2.waitKey(0)


if __name__ == '__main__':
  main()
