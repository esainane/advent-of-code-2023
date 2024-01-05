#!/usr/bin/env python3

from collections import defaultdict
import functools
from sys import stderr, stdin
from typing import List

def d(*args, **kwargs):
    print(file=stderr, *args, **kwargs)
    pass

valid_next_directions = {
    '>': ((1, 0),),
    '<': ((-1, 0),),
    '^': ((0, -1),),
    'v': ((0, 1),),
    '.': ((1, 0), (-1, 0), (0, 1), (0, -1)),
}

class Node(object):
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.edges = []

    def __hash__(self) -> int:
        return hash((self.x, self.y))
    
    def __eq__(self, other) -> bool:
        return self.x == other.x and self.y == other.y

class Grid(object):
    def __init__(self, input_data: List[str]):
        self.grid = input_data

    def find_start(self):
        y = 0
        x = self.grid[y].index('.')
        assert(x != -1)
        return (x, y)

    def find_end(self):
        y = len(self.grid) - 1
        x = self.grid[y].index('.')
        assert(x != -1)
        return (x, y)

    def longest_path(self, start, end):
        # First, scan the grid to transform very long paths into abstract
        # edges with a weight equal to the number of steps in the path.
        nodes = defaultdict(list)
        # (pos, distance since last node, seen coordinates, previous node)
        to_visit = [(start, 0, set(), start)]

        d("Running simplification pass")

        while to_visit:
            pos, dist, visited, prev = to_visit.pop(0)
            x, y = pos
            if pos == end:
                # Connect to our previous node
                nodes[pos].append((prev, dist))
                nodes[prev].append((pos, dist))
                # Can't continue past the exit, this path is done
                continue
            assert(pos not in visited)
            visited.add(pos)
            outbound_count = 0
            for dx, dy in valid_next_directions[self.grid[y][x]]:
                nx, ny = x + dx, y + dy
                if nx < 0 or nx >= len(self.grid[0]):
                    continue
                if ny < 0 or ny >= len(self.grid):
                    continue
                if (nx, ny) in visited:
                    continue
                if self.grid[ny][nx] == '#':
                    continue
                if outbound_count == 1:
                    # We now have an intersection!
                    # Grab the last seeker we just sent out, and make it
                    # point to this new intersection
                    opos, odist, ovisited, oprev = to_visit.pop()
                    to_visit.append((opos, 1, ovisited, pos))
                    # Connect to our previous node
                    nodes[pos].append((prev, dist))
                    nodes[prev].append((pos, dist))
                    outbound_count += 1
                elif outbound_count == 0:
                    # We have a new outbound path
                    outbound_count += 1
                    to_visit.append(((nx, ny), dist + 1, visited, prev))
                    continue
                # Add another branch to our intersection
                to_visit.append(((nx, ny), 1, visited.copy(), pos))

        d("Rendering graph state")
        # self._render_graph(nodes, '23p2.png')

        # Another simplification pass: If a node has two edges to the same
        # node, they can be combined into a single edge (with the longest path)
        for node, edges in nodes.items():
            map = {}
            for edge in edges:
                if edge[0] in map:
                    map[edge[0]] = max(map[edge[0]], edge[1])
                else:
                    map[edge[0]] = edge[1]
            nodes[node] = [(k, v) for k, v in map.items()]

        # self._render_graph(nodes, '23p2-simplified.png')

        # This simplified graph is now brute forcable.
        # Run pathfinding, over the simplified graph we just made.

        # Slight cheese: We know that there is one node in front of
        # the exit, so any path that reaches this penultimate node
        # can terminate as if it was the exit, and we can add the
        # cost from the penultimate node and the exit to the initial
        # cost. This prunes a surprising amount of search space
        end, weight = nodes[end][0]

        d("Running solver pass")

        bit_index = {}
        for i, node in enumerate(nodes.keys()):
            bit_index[node] = i

        # (node, distance, visited)
        to_visit = [(start, weight, 0)]
        total_dist = 0
        while to_visit:
            pos, dist, visited = to_visit.pop()
            #d(pos, dist)
            bitflag = 1 << bit_index[pos]
            assert(not (visited & bitflag))
            visited |= bitflag
            if pos == end:
                total_dist = max(total_dist, dist)
                # Can't continue past the exit, this path is done
                continue
            for next, weight in nodes[pos]:
                if visited & (1 << bit_index[next]):
                    continue
                to_visit.append((next, dist + weight, visited))
        return total_dist
    
    def _render_graph(self, nodes, filename):
        import pydot
        graph = pydot.Dot()

        for node, edges in nodes.items():
            n = pydot.Node(str(node))
            graph.add_node(n)
            for edge in edges:
                e = pydot.Edge(str(node), str(edge[0]), label=str(edge[1]))
                graph.add_edge(e)
        
        graph.write_png(filename)

def main():
    input_data = [line.rstrip() for line in stdin.read().splitlines()]
    grid = Grid(input_data)

    start = grid.find_start()
    end = grid.find_end()
    print(grid.longest_path(start, end))


if __name__ == '__main__':
    main()
