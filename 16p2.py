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
        self.width = len(input_data[0])
        self.height = len(input_data)

    def trace(self, coordinates, direction):
        energized = [[False for _ in range(self.width)] for _ in range(self.height)]
        self._trace(coordinates, direction, set(), energized)
        return self._energized_count(energized)

    def _trace(self, coordinates, direction, spawned, energized):
        if (coordinates, direction) in spawned:
            return
        spawned.add((coordinates, direction))
        x, y = coordinates
        dx, dy = direction

        while 0 <= x < self.width and 0 <= y < self.height:
            energized[y][x] = True
            tile = self.grid[y][x]
            if tile == '/':
                dx, dy = -dy, -dx
            elif tile == '\\':
                dx, dy = dy, dx
            elif tile == '-':
                if dx == 0:
                    # Split into two directions
                    self._trace((x - 1, y), (-1, 0), spawned, energized)
                    self._trace((x + 1, y), (1, 0), spawned, energized)
                    return
            elif tile == '|':
                if dy == 0:
                    # Split into two directions
                    self._trace((x, y - 1), (0, -1), spawned, energized)
                    self._trace((x, y + 1), (0, 1), spawned, energized)
                    return
            else:
                assert(tile == '.')
            x += dx
            y += dy

    def try_traces(self):
        for i in range(self.width):
            yield self.trace((i, 0), (0, 1))
            yield self.trace((i, self.height - 1), (0, -1))
        for i in range(self.height):
            yield self.trace((0, i), (1, 0))
            yield self.trace((self.width - 1, i), (-1, 0))

    def _energized_count(self, energized):
        return sum(sum(row) for row in energized)



def main():
    input_data = [line.rstrip() for line in stdin]
    data = Document(input_data)

    print(max(data.try_traces()))


if __name__ == '__main__':
    main()
