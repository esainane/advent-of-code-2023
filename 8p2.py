#!/usr/bin/env python3

from collections import defaultdict
import heapq
from itertools import chain, cycle
from functools import reduce
from sys import stdin
from typing import List

from pyparsing import alphanums, delimitedList, Group, Keyword, White, Word, ZeroOrMore

directions = Word('LR')
node = Word(alphanums)
edgelist = Group(node('source') + "=" + "(" + delimitedList(node)('targets') + ")")
document = directions('directions') + ZeroOrMore(edgelist)('graph')

counter = 0
def print_sometimes(*args, **kwargs):
    global counter
    if counter % 1000000 == 0:
        print(*args, **kwargs)
    counter += 1

class Document(object):
    def __init__(self, input_data: str):
        data = document.parse_string(input_data, parse_all=True)
        self.directions = data.directions
        self.vertices = {}
        for vertex in data.graph:
            self.vertices[vertex.source] = (vertex.targets[0], vertex.targets[1])

    def walk(self, start, end_criteria):
        '''
        Walk the graph, following the directions, and repeating as needed.

        Returns the number of steps taken to reach the specified target.
        '''
        current_name = start
        for step, d in enumerate(cycle(self.directions)):
            if end_criteria(current_name):
                return step
            current = self.vertices[current_name]
            if d == 'L':
                current_name = current[0]
            elif d == 'R':
                current_name = current[1]
            else:
                raise ValueError(f'Unknown direction {d}')

    def walk_all(self, start_criteria, end_criteria):
        '''
        Walk the graph, following the directions, and repeating as needed.

        Returns the number of steps taken to reach the specified targets.
        '''
        # Maintain a cache from each node to the number of new steps required
        # to reach an end node, and the end node reached.
        # Note that here we take advantage of a property of the dataset not
        # guaranteed by the problem statement: the step offset is always 0.
        # Indexing is node_name -> (steps, end_node)
        cache = {}
        cache_stats = [0, 0] # misses, total
        def walk_from(start):
            # Walk from the given node at the given step offset until we reach
            # an end node, taking at least one step, and return the number of
            # steps taken and the end node reached.
            #step_offset = step_offset % len(self.directions)
            cache_stats[1] += 1
            if start in cache:
                return cache[start]
            cache_stats[0] += 1
            current_name = start
            for step, d in enumerate(cycle(self.directions)):
                current = self.vertices[current_name]
                if d == 'L':
                    current_name = current[0]
                elif d == 'R':
                    current_name = current[1]
                else:
                    raise ValueError(f'Unknown direction {d}')
                if end_criteria(current_name):
                    result = (step + 1, current_name)
                    cache[start] = result
                    return result
        # Find all starting nodes
        current_names = [k for k in self.vertices.keys() if start_criteria(k)]

        # Find the first accepting node from each starting node
        results = [walk_from(start) for start in current_names]


        # Note that here we take advantage of a property of the dataset not
        # guaranteed by the problem statement: the next step for each accepting
        # node is itself, with the same length as the initial path, meaning
        # every starting node follows an absurdly simple cycle. This means
        # we can get away with using the lowest common multiple to find the
        # solution.

        # ......this is extremely anticlimatic.
        assert(all((s,n) == walk_from(n) for s,n in results))

        def gcd(a, b):
            while b:
                a, b = b, a % b
            return a
        # Find the lowest common multiple of all the step counts.
        lcm = reduce(lambda a, b: a * b // gcd(a, b), (s for s,n in results))
        print(f'lcm({[s for s,n in results]}) = {lcm}')
        return lcm





input_data = '\n'.join(line.rstrip() for line in stdin)
data = Document(input_data)

print(data.walk_all(lambda x: x.endswith('A'), lambda x: x.endswith('Z')))
