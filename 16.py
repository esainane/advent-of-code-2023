#!/usr/bin/env python3

from collections import defaultdict
from itertools import chain
from sys import argv, stderr, stdin
from typing import Dict, Iterable, List, Tuple

def d(*args, **kwargs):
    #print(file=stderr, *args, **kwargs)
    pass

class Document(object):
    def __init__(self, input_data: List[str]):
        self.grid = input_data
        width = len(input_data[0])
        height = len(input_data)
        self.energized = [[False for _ in range(width)] for _ in range(height)]
        self.width = width
        self.height = height

    def trace(self, coordinates, direction, spawned=set()):
        if (coordinates, direction) in spawned:
            return
        spawned.add((coordinates, direction))
        x, y = coordinates
        dx, dy = direction

        while 0 <= x < self.width and 0 <= y < self.height:
            self.energized[y][x] = True
            tile = self.grid[y][x]
            if tile == '/':
                dx, dy = -dy, -dx
            elif tile == '\\':
                dx, dy = dy, dx
            elif tile == '-':
                if dx == 0:
                    # Split into two directions
                    self.trace((x - 1, y), (-1, 0), spawned)
                    self.trace((x + 1, y), (1, 0), spawned)
                    return
            elif tile == '|':
                if dy == 0:
                    # Split into two directions
                    self.trace((x, y - 1), (0, -1), spawned)
                    self.trace((x, y + 1), (0, 1), spawned)
                    return
            else:
                assert(tile == '.')
            x += dx
            y += dy

    def print_energized(self):
        for y, row in enumerate(self.energized):
            d(''.join(self.grid[y][x] if cell else ' ' for x, cell in enumerate(row)))

    def energized_count(self):
        return sum(sum(row) for row in self.energized)



def main():
    input_data = [line.rstrip() for line in stdin]
    data = Document(input_data)

    data.trace((0,0), (1,0))
    data.print_energized()

    print(data.energized_count())


if __name__ == '__main__':
    main()
