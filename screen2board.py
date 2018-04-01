from __future__ import print_function
import numpy as np
import cv2
import math
import algemy


# Pixel locations for the top of the board for each board width.
# Based on 1080x1920 display resolution on Nexus 5X.
BOARD_TOP = {
    4: ((139, 605), (951, 605)),
    5: ((112, 580), (960, 580)),
    6: ((102, 570), (980, 570)),
    7: ((92, 560), (987, 560)),
}

DILATE = 0.2
WHEEL_RF = 0.75


# Average colors for each board crystal.
COLOR_MAP = {
  ' ': (255, 255, 255),
  'R': (135, 135, 178),
  'O': (87, 136, 177),
  'Y': (130, 174, 174),
  'G': (82, 136, 82),
  'B': (175, 145, 145),
  'V': (162, 90, 162),
  'W': (214, 214, 214),
  'X': (34, 66, 99),
}

COLORS = ['R', 'O', 'Y', 'G', 'B', 'V']


def closest_color(r, g, b):
  v = 255
  ret = ''
  for c, (r2, g2, b2) in COLOR_MAP.items():
    d = math.sqrt((r - r2)**2 + (g - g2)**2 + (b - b2)**2)
    if d < v:
      v = d
      ret = c
  return ret


def main():
  # TODO: make args
  img = cv2.imread('/tmp/screen.png')
  board_size = 7
  expanded_colors = True

  ##

  top_line = BOARD_TOP[board_size]

  top_left = top_line[0]
  top_width = top_line[1][0] - top_line[0][0]
  box_width = top_width / board_size

  grid = {}
  for r in range(board_size):
    for c in range(board_size):
      x = int(top_left[0] + box_width/2 + box_width * c)
      y = int(top_left[1] + box_width/2 + box_width * r)
      dilate = int(box_width * DILATE)
      sample = img[(y-dilate):(y+dilate), (x-dilate):(x+dilate)]
      avg_color = tuple(np.mean(sample, axis=(0,1)))
      color = closest_color(*avg_color)
      grid[(r,c)] = color

  board = [] 
  for r in range(board_size):
    board.append([grid[(r,c)] for c in range(board_size)])

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

  for r in range(board_size):
    for c in range(board_size):
      x = int(top_left[0] + box_width/2 + box_width * c)
      y = int(top_left[1] + box_width/2 + box_width * r)

      color = solution[r][c]
      if color.strip() == '':
        continue

      # Tap on square to bring up color wheel.
      print("adb shell input tap %i %i" % (x, y))

      deg = (360 / len(COLORS)) * COLORS.index(color)
      xd = math.sin(math.radians(deg)) * WHEEL_RF * box_width
      yd = -1 * math.cos(math.radians(deg)) * WHEEL_RF * box_width

      # Tap on the correct color.
      print("adb shell input tap %i %i" % (x + xd, y + yd))


if __name__ == '__main__':
  main()
