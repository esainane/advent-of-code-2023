#!/usr/bin/env python3

from collections import defaultdict
import re
from sys import stdin
from typing import List, Tuple

class Number(object):
    def __init__(self, y, x_start, x_end, value):
        '''
        Stores a number found in the grid.

        x_start is inclusive, x_end is exclusive
        '''
        self.y = y
        self.x_start = x_start
        self.x_end = x_end
        self.value = value

class Part(object):
    def __init__(self):
        self.values: List[int] = []
    def update(self, y, x, kind, value):
        '''
        Stores a part found in the grid.
        '''
        self.y = y
        self.x = x
        self.kind = kind
        self.values.append(value)

class Schematic(object):
    number_finder = re.compile(r'\d+')
    symbol_finder = re.compile(r'[^.\d]')
    def __init__(self, grid):
        # Find any contiguous numbers in the input
        # Treat our input as a 2D grid of characters

        # Find the width and height of the grid
        self.width = len(grid[0])
        self.height = len(grid)

        # Save the grid for later reference
        self.grid = grid
        self.parts = defaultdict(lambda: defaultdict(Part))

        # Find all numbers in the grid. Store their coordinates and values.
        self.numbers: List[Number] = []
        for y in range(self.height):
            for m in self.number_finder.finditer(grid[y]):
                n = Number(y, m.start(), m.end(), int(m.group(0)))
                adj = self.is_part_number(n)
                for p in adj:
                    self.parts[p[1]][p[2]].update(p[1], p[2], p[0], n.value)
                self.numbers.append(n)

    def is_part_number(self, n: Number) -> List[Tuple[str, int, int]]:
        '''
        A number in the schematic is considered a part number if it any digit
        is adjacent to a non-'.', non-digit symbol, including diagonally.
        '''
        result = []
        # Check around the number from the column before to the column after
        start = max(0, n.x_start - 1)
        end = n.x_end + 1
        #print('Checking around number', n.value, 'from', n.y, start, end)
        # Check the rows above, on, and below the number
        for y in range(n.y - 1, n.y + 2):
            if y < 0 or y >= self.height:
                continue
            sub = self.grid[y][start:end]
            #print('Checking for symbols in', sub)
            m = self.symbol_finder.search(sub)
            if m:
                #print(f'Number {n.value} at ({n.y}, {n.x_start}:{n.x_end}) is a part number - adjacent to symbol {m.group(0)} at ({y}, {m.start() + start})')
                result.append((m.group(0), y, m.start() + start))
        #print(f'Number {n.value} at ({n.y}, {n.x_start}:{n.x_end}) is not a part number')
        return result

    def part_numbers(self):
        '''
        Return the part numbers found in the schematic.
        '''
        return [n for n in self.numbers if self.is_part_number(n)]

    def is_gear(self, p: Part) -> bool:
        '''
        A part is considered a gear if it is a '*' symbol and adjacent to
        exactly two part numbers.
        '''
        return p.kind == '*' and len(p.values) == 2

    def gears(self):
        '''
        Return all gears found in the schematic.
        '''
        return [p for yp in self.parts.values() for p in yp.values() if self.is_gear(p)]

# Parse input
s = Schematic([line.rstrip() for line in stdin.readlines()])

# Print the sum of all part numbers
print(sum(p.values[0] * p.values[1] for p in s.gears()))
