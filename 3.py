#!/usr/bin/env python3

import re
from sys import stdin
from typing import List

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

        # Find all numbers in the grid. Store their coordinates and values.
        self.numbers: List[Number] = []
        for y in range(self.height):
            for m in self.number_finder.finditer(grid[y]):
                self.numbers.append(Number(y, m.start(), m.end(), int(m.group(0))))

    def is_part_number(self, n: Number):
        '''
        A number in the schematic is considered a part number if it any digit
        is adjacent to a non-'.', non-digit symbol, including diagonally.
        '''
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
                #print(f'Number {n.value} at ({n.y + 1}, {n.x_start}:{n.x_end}) is a part number - adjacent to symbol {m.group(0)} at ({y + 1}, {m.start() + start})')
                return True
        #print(f'Number {n.value} at ({n.y + 1}, {n.x_start}:{n.x_end}) is not a part number')
        return False

    def part_numbers(self):
        '''
        Return the part numbers found in the schematic.
        '''
        return [n for n in self.numbers if self.is_part_number(n)]

# Parse input
s = Schematic([line.rstrip() for line in stdin.readlines()])

# Print the sum of all part numbers
print(sum(n.value for n in s.part_numbers()))
