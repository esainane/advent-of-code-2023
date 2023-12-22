#!/usr/bin/env python3

from collections import defaultdict
from itertools import chain
from sys import argv, stderr, stdin
from typing import Dict, Iterable, List, Tuple

from pyparsing import alphanums, delimitedList, nums, Group, Keyword, White, Word, ZeroOrMore

number = Word(nums)
hexnum = Word('0123456789abcdef')
direction = Keyword('U') | Keyword('D') | Keyword('L') | Keyword('R')
dig_list = Group(direction('direction') + number('distance') + '(#' + hexnum('group') + ')')
document = ZeroOrMore(dig_list)('edges')

def d(*args, **kwargs):
    #print(file=stderr, *args, **kwargs)
    pass

# Note that much of problem 18 is the construction of problem 10

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


def cell_from_directions(d1, d2) -> str:
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

def direction_from_dig_instruction(dig_dir: str) -> Direction:
    if dig_dir == 'U':
        return north
    elif dig_dir == 'D':
        return south
    elif dig_dir == 'L':
        return west
    elif dig_dir == 'R':
        return east
    else:
        raise ValueError(f'Unknown direction {dig_dir}')


class Document(object):
    def __init__(self, input_data: str):
        self.data = document.parse_string(input_data, parse_all=True)

    def build_loop(self):
        dimensions, origin = self.find_bounds()
        w, h = dimensions
        x, y = origin
        self.grid = grid = [[' ' for _ in range(w)] for _ in range(h)]
        last_dir = direction_from_dig_instruction(self.data.edges[-1].direction).opposite
        for edge in self.data.edges:
            distance = int(edge.distance)
            dir = direction_from_dig_instruction(edge.direction)
            for i in range(distance):
                cell = cell_from_directions(last_dir, dir)
                d(x, y, cell)
                assert(grid[y][x] == ' ')
                grid[y][x] = cell
                last_dir = dir
                x += dir.dx
                y += dir.dy
            last_dir = last_dir.opposite

    def count_contained_cells(self) -> int:
        '''
        Count the number of cells in the grid that are contained within the
        loop.

        We do this by casting a ray for each row, and counting each cell
        including those part of the loop, which comes after an odd number of 
        vertical edges.

        We must have previously found the main loop.
        '''
        count = 0
        w, h = len(self.grid[0]), len(self.grid)
        self.contained_cells = [[0 for _ in range(w)] for _ in range(h)]
        for y, row in enumerate(self.grid):
            # Count the number of cells in this row that are contained
            # within the loop
            in_loop = False
            half_vpipe = 0
            for x, cell in enumerate(row):
                if cell == '|':
                    count += 1
                    in_loop = not in_loop
                # Keep track of "half" vertical pipes. If the pipe turns
                # turns back to the direction it comes from, it cancels out.
                # If it continues down, complete it to make a full edge.
                elif cell in 'FJ':
                    count += 1
                    half_vpipe -= 1
                    if half_vpipe <= -2:
                        in_loop = not in_loop
                        half_vpipe += 2
                elif cell in 'L7':
                    count += 1
                    half_vpipe += 1
                    if half_vpipe >= 2:
                        in_loop = not in_loop
                        half_vpipe -= 2
                # Horizontal pipes between "half" vertical pipes don't affect
                # anything
                elif cell == '-':
                    count += 1
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

    def find_bounds(self) -> Tuple[Tuple[int, int], Tuple[int, int]]:
        '''
        Find the bounding dimensions of the grid, and the origin's coordinates
        within them.
        '''
        x_min = 0
        x_max = 0
        y_min = 0
        y_max = 0
        x = 0
        y = 0
        for edge in self.data.edges:
            distance = int(edge.distance)
            direction = direction_from_dig_instruction(edge.direction)
            x += direction.dx * distance
            y += direction.dy * distance
            x_min = min(x_min, x)
            x_max = max(x_max, x)
            y_min = min(y_min, y)
            y_max = max(y_max, y)

        x_max += 1
        y_max += 1

        d(f"Bounds: {x_min}, {x_max}, {y_min}, {y_max} -> {-x_min + x_max}, {-y_min + y_max}, {-x_min}, {-y_min}")

        return ((-x_min + x_max, -y_min + y_max), (-x_min, -y_min))



def main():
    input_data = '\n'.join(line.rstrip() for line in stdin.read().splitlines())
    document = Document(input_data)

    d(document.data)

    document.build_loop()

    d('\n'.join(''.join(line) for line in document.grid))

    print(document.count_contained_cells())

if __name__ == '__main__':
    main()
