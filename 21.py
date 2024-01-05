#!/usr/bin/env python3

import functools
from sys import stderr, stdin
from typing import List

def d(*args, **kwargs):
    print(file=stderr, *args, **kwargs)
    pass

class Grid(object):
    def __init__(self, input_data: List[List[str]]):
        self.grid = input_data

    def count_reachable_plots(self, max_distance=64) -> int:
        # First, find the starting position, a cell 'S'
        for y, row in enumerate(self.grid):
            for x, cell in enumerate(row):
                if cell == 'S':
                    starting_position = (x, y)
                    break
            else:
                continue
            break
        else:
            raise ValueError('No starting position found')

        exact_reachable = 0

        # Now, do a breadth-first search to find all reachable cells
        visited = set()
        to_visit = [(starting_position, max_distance)]
        while to_visit:
            pos, dist = to_visit.pop(0)
            x, y = pos
            if (x, y) in visited:
                continue
            visited.add((x, y))
            if dist % 2 == 0:
                exact_reachable += 1
                self.grid[y][x] = "O"
            if dist == 0:
                continue
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                nx, ny = x + dx, y + dy
                if nx < 0 or nx >= len(self.grid[0]):
                    continue
                if ny < 0 or ny >= len(self.grid):
                    continue
                if (nx, ny) in visited:
                    continue
                if self.grid[ny][nx] == '#':
                    continue
                to_visit.append(((nx, ny), dist - 1))

        return exact_reachable

    def display(self):
        for row in self.grid:
            d(''.join(row))

def main():
    input_data = [[c for c in line.rstrip()] for line in stdin.read().splitlines()]
    grid = Grid(input_data)

    grid.display()

    print(grid.count_reachable_plots())

    grid.display()


if __name__ == '__main__':
    main()
