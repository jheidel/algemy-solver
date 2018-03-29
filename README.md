<aside class="warning">
This project is a work in progress and not yet functional.
</aside>

# About

Algemy is a logic game. "Light sources" are placed on the board in order to
illuminate a set of crystals. Each crystal must be set to a certain color, and
the entire board must be covered by light.

 - [Google Play](https://play.google.com/store/apps/details?id=com.KennyYoung.AlgemyGame)
 - [Apple App Store](https://itunes.apple.com/us/app/algemy/id1355522887?mt=8)

This project defines a solver of this game (which could be useful for [Puzzle Hunt 19](https://puzzlehunt.research.microsoft.com/19/)).

# TODO

 - [x] Initial documentation
 - [ ] Initial implementation (square board)
 - [ ] Complex color mixing
 - [ ] Hexagonal board

# Dependencies

Tested working on Ubuntu 17.10.

```shell
# Python 2
sudo apt-get install python-pip
pip install ortools

# Python 3
sudo apt-get install python3-pip
pip3 install ortools
```

# Solving Methodology

## Background

Algemy can be modeled as a [Constraint Satisfaction Problem (CSP)](https://en.wikipedia.org/wiki/Constraint_satisfaction_problem).

Google provides a [CSP solver library](https://developers.google.com/optimization/cp/cp_solver) as part of its optimization tools which we use to implement this CSP problem. The Google documentation has some educational material that's useful for understanding these types of problems, such as the [N-queens example](https://developers.google.com/optimization/cp/queens).

## Constraints

The CSP solver requires defining the problem as a set of constraints about possible solutions.

Each empty square in a board is mapped to an integer variable that can either
be unset (0 value) or a light source (positive value, mapped from color).

For example, consider this board:

[TODO]

#### All "sight-lines" have at most one light source

[TODO]

#### Each crystal is illuminated one or more light sources of the correct color(s)

[TODO]

#### Each square is either a light source, or has a light source in its "sight-lines"

[TODO]

