#!/usr/bin/env python3

from sys import stderr, stdin
from typing import Dict, Iterable, List, Tuple

def d(*args, **kwargs):
    pass
    #print(file=stderr, *args, **kwargs

class Direction(object):
    def __init__(self, dx: int, dy: int):
        self.dx = dx
        self.dy = dy

    def set_turn_mapping(self, mapping: Dict[str, 'Direction']):
        self.turn_mapping = mapping

    def __iter__(self) -> Iterable[int]:
        yield self.dx
        yield self.dy

    def __repr__(self):
        return f'Direction({self.dx}, {self.dy})'

north = Direction(0, -1)
south = Direction(0, 1)
east = Direction(1, 0)
west = Direction(-1, 0)

north.set_turn_mapping({'|': north, 'F': east, '7': west})
south.set_turn_mapping({'|': south, 'L': east, 'J': west})
east.set_turn_mapping({'-': east, '7': south, 'J': north})
west.set_turn_mapping({'-': west, 'F': south, 'L': north})

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
                    return (x, y)
    
    def find_main_loop(self, start: Tuple[int, int]):
        '''
        From a specified starting location, find two adjacent cells that are
        part of the same connected component. Return the total length of the
        loop this forms.
        '''
        w, h = len(self.cells[0]), len(self.cells)
        # Iterate through the four cardinally adjacent cells, tracing a path
        for dir in (north, south, east, west):
            # Calculate the location of the adjacent cell
            distance = 0
            x, y = start
            while True:
                d(f'Checking {x}, {y} going {dir}')
                dx, dy = dir
                x += dx
                y += dy
                # If it's out of bounds, end this trace
                if not (0 <= x < w and 0 <= y < h):
                    break
                distance += 1
                # If we found the start, we're done
                if (x, y) == start:
                    return distance
                cell = self.cells[y][x]
                # If it's empty, end this trace
                if cell == '.':
                    break
                # Otherwise, work out which direction we're turning next
                try:
                    dir = dir.turn_mapping[cell]
                except KeyError:
                    # Not connected to us, end this trace
                    break
        raise ValueError('No loop found')





input_data = list(line.rstrip() for line in stdin)
data = Maze(input_data)

# Print out the distance to the furtherest element in the cycle
print(data.find_main_loop(data.find_source()) // 2)
