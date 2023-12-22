#!/usr/bin/env python3

from collections import defaultdict
from heapq import heappush, heappop
from itertools import chain
from sys import argv, stderr, stdin
from typing import Dict, Iterable, List, Set, Tuple

# Represent the search space as a graph, where each node is a coordinate and
# direction, and each edge is a move from one node to another.
# A node is the complete set of information required to resume a search, while
# we store a subset of information to avoid duplicating work in SearchCoord.

class SearchCoord(object):
    def __init__(self, coordinates, direction, straight_length=0):
        self.coordinates = coordinates
        self.direction = direction
        self.straight_length = straight_length

    def __hash__(self):
        return hash((self.coordinates, self.direction, self.straight_length))

    def __eq__(self, other):
        return (self.coordinates, self.direction, self.straight_length) == (other.coordinates, other.direction, other.straight_length)

    def __repr__(self):
        return f'<SearchCoord {self.coordinates} {self.direction} {self.straight_length}>'

class SearchNode(object):
    def __init__(self, coordinates, direction, straight_length=0, weight=0, heuristic=0, parent=None):
        self.coord = SearchCoord(coordinates, direction, straight_length)
        self.weight = weight
        self.heuristic = heuristic
        self.parent = parent

    def __lt__(self, other):
        return (self.weight + self.heuristic) < (other.weight + other.heuristic)

    def __repr__(self):
        return f'<SearchNode {self.coord} {self.weight} {self.heuristic}>'

ordinals = ((0, 1), (0, -1), (1, 0), (-1, 0))

class Document(object):
    def __init__(self, input_data: List[List[int]]):
        self.grid = input_data
        self.width = len(input_data[0])
        self.height = len(input_data)

    def path_find(self, start, goal, straight_limit=3) -> List[SearchNode]:
        '''
        Perform a modified A* search, where we move no more than straight_limit
        spaces in a straight line at a time
        '''
        fake_dir = (314,314)
        root = SearchNode(start, fake_dir)
        queue: List[SearchNode] = [root]
        visited: Set[SearchCoord] = set()
        while queue:
            node = heappop(queue)
            if node.coord.coordinates == goal:
                # Found a path
                path = []
                while node.parent:
                    path.append(node)
                    node = node.parent
                path.append(node)
                path.reverse()
                return path
            if node.coord in visited:
                continue
            visited.add(node.coord)
            for next_node in self._expand(node, straight_limit, goal):
                if next_node.coord in visited:
                    continue
                heappush(queue, next_node)
    
    def path_cost(self, path: List[SearchNode]) -> int:
        '''
        Return the total cost of the given path.
        '''
        return path[-1].weight

    def _expand(self, node, straight_limit, goal):
        '''
        Yield each node adjacent to the given node, without moving more than
        straight_limit spaces in a straight line.
        '''
        x, y = node.coord.coordinates
        odx, ody = node.coord.direction
        straight_length = node.coord.straight_length
        for next_dir in ordinals:
            continuing_straight = next_dir == node.coord.direction
            if continuing_straight and straight_length == straight_limit:
                # We can't move any further in this direction
                continue
            dx, dy = next_dir
            if odx == -dx and ody == -dy:
                # We can't move backwards
                continue
            nx, ny = x + dx, y + dy
            if not (0 <= nx < self.width and 0 <= ny < self.height):
                # We can't move off the grid
                continue
            next_node = SearchNode(
                (nx, ny),
                next_dir,
                straight_length + 1 if continuing_straight else 1,
                node.weight + self.grid[y + dy][x + dx],
                self._heuristic((x + dx, y + dy), goal),
                node
            )
            yield next_node

    def _heuristic(self, coordinates, goal):
        '''
        Return the taxicab distance from the coordinates to the goal.
        '''
        x, y = coordinates
        gx, gy = goal
        return abs(x - gx) + abs(y - gy)

    def print_path(self, path: List[SearchNode]):
        '''
        Print the grid with the given path overlaid on top.
        '''
        grid = [[str(cell) for cell in row] for row in self.grid]
        for node in path:
            x, y = node.coord.coordinates
            grid[y][x] = '*'
        for row in grid:
            print(''.join(row))


def main():
    input_data = [[int(c) for c in line.rstrip()] for line in stdin]
    data = Document(input_data)

    path = data.path_find((0,0), (data.width - 1, data.height - 1))

    #data.print_path(path)
    #print(path)

    print(data.path_cost(path))


if __name__ == '__main__':
    main()
