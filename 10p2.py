#!/usr/bin/env python3

from sys import stderr, stdin
from typing import Dict, Iterable, List, Tuple

def d(*args, **kwargs):
    pass
    #print(file=stderr, *args, **kwargs

class Direction(object):
    def __init__(self, dx: int, dy: int, straight_repr: str):
        self.dx = dx
        self.dy = dy
        self.straight_repr = straight_repr

    def set_turn_mapping(self, mapping: Dict[str, 'Direction']):
        self.turn_mapping = mapping

    def set_opposite(self, opposite: 'Direction'):
        self.opposite = opposite
        opposite.opposite = self

    def __iter__(self) -> Iterable[int]:
        yield self.dx
        yield self.dy

    def __repr__(self):
        return f'Direction({self.dx}, {self.dy}, "{self.straight_repr}")'

north = Direction(0, -1, '|')
south = Direction(0, 1, '|')
east = Direction(1, 0, '-')
west = Direction(-1, 0, '-')

north.set_turn_mapping({'|': north, 'F': east, '7': west})
south.set_turn_mapping({'|': south, 'L': east, 'J': west})
east.set_turn_mapping({'-': east, '7': south, 'J': north})
west.set_turn_mapping({'-': west, 'F': south, 'L': north})

north.set_opposite(south)
east.set_opposite(west)

def cell_from_direcctions(d1, d2) -> str:
    '''
    Return a cell connected to two provided directions.
    '''
    if d1 == d2:
        return d1.straight_repr
    bend = set((d1, d2))
    if bend == set((north, east)):
        return 'L'
    elif bend == set((north, west)):
        return 'J'
    elif bend == set((south, east)):
        return 'F'
    elif bend == set((south, west)):
        return '7'
    else:
        raise ValueError(f'Unknown directions {d1}, {d2}')

class Maze(object):
    def __init__(self, input_data: List[str]):
        '''
        Straight pipes are labelled - and |, corners are labelled F 7 L and J.

        Empty spaces are labelled ., and the start is labelled S.
        '''
        self.cells = input_data

    def find_source(self) -> Tuple[int, int]:
        '''
        Find the cell labelled "S"
        '''
        for y, row in enumerate(self.cells):
            for x, cell in enumerate(row):
                if cell == 'S':
                    d(f'Found source at {x}, {y}')
                    self.source = (x, y)
                    return self.source

    def find_main_loop(self) -> int:
        '''
        From a specified starting location, find two adjacent cells that are
        part of the same connected component. Return the total length of the
        loop this forms.
        '''
        w, h = len(self.cells[0]), len(self.cells)
        # Iterate through the four cardinally adjacent cells, tracing a path
        for sdir in (north, south, east, west):
            dir = sdir
            # Calculate the location of the adjacent cell
            distance = 0
            x, y = self.source
            self.loop_cells = [[' ' for _ in range(w)] for _ in range(h)]
            while True:
                d(f'Checking {x}, {y} going {dir}')
                dx, dy = dir
                x += dx
                y += dy
                # If it's out of bounds, end this trace
                if not (0 <= x < w and 0 <= y < h):
                    break
                distance += 1
                cell = self.cells[y][x]
                # If it's empty, end this trace
                if cell == '.':
                    break
                # If we found the start, first replace it with a standard pipe
                # label based on its directions
                if (x, y) == self.source:
                    d(f'Left start going {sdir}, arrived back at start going {dir}', file=stderr)
                    cell = cell_from_direcctions(sdir, dir.opposite)
                self.loop_cells[y][x] = cell
                # If we found the start, we're done
                if (x, y) == self.source:
                    return distance
                # Otherwise, work out which direction we're turning next
                try:
                    dir = dir.turn_mapping[cell]
                except KeyError:
                    # Not connected to us, end this trace
                    break
        raise ValueError('No loop found')

    def label_maze(self) -> Iterable[Iterable[str]]:
        for y, row in enumerate(self.loop_cells):
            yield self.label_row(y, row)

    def label_row(self, y, row):
        for x, cell in enumerate(row):
            if cell == ' ':
                yield 'x' if self.contained_cells[y][x] else ' '
            else:
                yield 'M' if self.contained_cells[y][x] else cell

    def count_contained_cells(self) -> int:
        '''
        Count the number of cells in the grid that are contained within the
        loop.

        We do this by casting a ray for each row, and counting each cell which
        is not itself part of the loop, and comes after an odd number of 
        vertical edges.

        We must have previously found the main loop.
        '''
        count = 0
        w, h = len(self.cells[0]), len(self.cells)
        self.contained_cells = [[0 for _ in range(w)] for _ in range(h)]
        for y, row in enumerate(self.loop_cells):
            # Count the number of cells in this row that are contained
            # within the loop
            in_loop = False
            half_vpipe = 0
            for x, cell in enumerate(row):
                if cell == '|':
                    in_loop = not in_loop
                # Keep track of "half" vertical pipes. If the pipe turns
                # turns back to the direction it comes from, it cancels out.
                # If it continues down, complete it to make a full edge.
                elif cell in 'FJ':
                    half_vpipe -= 1
                    if half_vpipe <= -2:
                        in_loop = not in_loop
                        half_vpipe += 2
                elif cell in 'L7':
                    half_vpipe += 1
                    if half_vpipe >= 2:
                        in_loop = not in_loop
                        half_vpipe -= 2
                # Horizontal pipes between "half" vertical pipes don't affect
                # anything
                elif cell == '-':
                    continue
                elif cell != ' ':
                    raise ValueError(f'Unknown cell {cell}')
                else:
                    # Empty space
                    if not in_loop:
                        continue
                    self.contained_cells[y][x] = 1
                    d(f'Cell {x}, {y} is contained', file=stderr)
                    count += 1
        return count





input_data = list(line.rstrip() for line in stdin)
data = Maze(input_data)

# Print out the distance to the furtherest element in the cycle
data.find_source()
data.find_main_loop()

print(data.count_contained_cells())

d('\n'.join(''.join(r) for r in data.label_maze()), file=stderr)
