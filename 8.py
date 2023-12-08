#!/usr/bin/env python3

from itertools import cycle
from sys import stdin
from typing import List

from pyparsing import alphas, delimitedList, Group, Keyword, White, Word, ZeroOrMore

directions = Word('LR')
node = Word(alphas)
edgelist = Group(node('source') + "=" + "(" + delimitedList(node)('targets') + ")")
document = directions('directions') + ZeroOrMore(edgelist)('graph')

class Vertex(object):
    def __init__(self, name: str, edges: List[str]):
        self.name = name
        self.edges = edges

    def __repr__(self):
        return f'Vertex({self.name}, {self.edges})'

class Document(object):
    def __init__(self, input_data: str):
        data = document.parse_string(input_data, parse_all=True)
        self.directions = data.directions
        self.vertices = {}
        for vertex in data.graph:
            self.vertices[vertex.source] = Vertex(vertex.source, vertex.targets)

    def walk(self, start: str, end: str):
        '''
        Walk the graph, following the directions, and repeating as needed.

        Returns the number of steps taken to reach the specified target.
        '''
        current_name = start
        for step, d in enumerate(cycle(self.directions)):
            if current_name == end:
                return step
            current = self.vertices[current_name]
            if d == 'L':
                current_name = current.edges[0]
            elif d == 'R':
                current_name = current.edges[1]
            else:
                raise ValueError(f'Unknown direction {d}')

            if step > 1000000:
                raise ValueError('Too many steps')

input_data = '\n'.join(line.rstrip() for line in stdin)
data = Document(input_data)

print(data.walk('AAA', 'ZZZ'))
