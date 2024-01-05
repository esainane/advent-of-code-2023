#!/usr/bin/env python3

import functools
from sys import stderr, stdin
from typing import Any, Dict, List, Set

from pyparsing import alphanums, delimitedList, nums, Group, Iterable, Literal, OneOrMore, Optional, ParseResults, Tuple, Word


def d(*args, **kwargs):
    print(file=stderr, *args, **kwargs)
    pass


number = Word(nums)
name = Word(alphanums)

coord = number('x') + Literal(',') + number('y') + Literal(',') + number('z')

stick = Group(coord)('start') + Literal('~') + Group(coord)('end')

document = OneOrMore(Group(stick))('sticks')

down = (0, 0, -1)

Coord = Tuple[int, int, int]

class Stick(object):
    def __init__(self, start, end):
        self.start = start
        self.end = end

        sx, sy, sz = start
        ex, ey, ez = end

        dims = 0
        if sx != ex:
            dims += 1
        if sy != ey:
            dims += 1
        if sz != ez:
            dims += 1
        assert(dims <= 1)
        dx, dy, dz = ex - sx, ey - sy, ez - sz
        self.dir = tuple(v//abs(v) if v else 0 for v in (dx, dy, dz))

    def top_coords(self) -> Iterable[Coord]:
        if self.dir[2]:
            yield max(self.start, self.end)
        else:
            yield from self.all_coords()

    def bottom_coords(self) -> Iterable[Coord]:
        if self.dir[2]:
            yield min(self.start, self.end)
        else:
            yield from self.all_coords()

    def all_coords(self) -> Iterable[Coord]:
        pos = self.start
        yield pos
        while pos != self.end:
            pos = tuple(p + d for p, d in zip(pos, self.dir))
            yield pos

    def register(self, document: 'Document') -> None:
        for x,y,z in self.all_coords():
            document.grid[x][y][z] = self

    def unregister(self, document: 'Document') -> None:
        for x,y,z in self.all_coords():
            document.grid[x][y][z] = None

    def drop(self, document: 'Document') -> None:
        if self.dir[2]:
            x,y,z = max(self.start, self.end)
            document.grid[x][y][z] = None
            self._drop()
            x,y,z = min(self.start, self.end)
            document.grid[x][y][z] = self
        else:
            self.unregister(document)
            self._drop()
            self.register(document)

    def _drop(self):
        self.start = tuple(p + d for p, d in zip(self.start, down))
        self.end = tuple(p + d for p, d in zip(self.end, down))

    def __repr__(self):
        return f'Stick({self.start}, {self.end})>'


class Document(object):
    def __init__(self, input_data: str):
        self.sticks = []
        max_x, max_y, max_z = 0, 0, 0
        data = document.parse_string(input_data)
        for stick in data.sticks:
            start = (int(stick.start.x), int(stick.start.y), int(stick.start.z))
            end = (int(stick.end.x), int(stick.end.y), int(stick.end.z))
            max_x = max(max_x, start[0], end[0])
            max_y = max(max_y, start[1], end[1])
            max_z = max(max_z, start[2], end[2])
            self.sticks.append(Stick(start, end))
        self.sticks.sort(key=lambda s: tuple(s.bottom_coords()))
        self.grid = [[[None for _ in range(max_z + 1)] for _ in range(max_y + 1)] for _ in range(max_x + 1)]
        for stick in self.sticks:
            stick.register(self)

    def can_drop(self, stick: Stick, ignore: Set[Stick] = set()) -> bool:
        for x,y,z in stick.bottom_coords():
            if z == 0:
                return False
            beneath = self.grid[x][y][z - 1]
            if beneath is not None and beneath not in ignore:
                return False
        return True

    def supporting(self, stick: Stick) -> Iterable[Stick]:
        max_z = len(self.grid[0][0]) - 1
        visited = set()
        for x,y,z in stick.top_coords():
            if z == max_z:
                continue
            above = self.grid[x][y][z + 1]
            if above is not None:
                if above in visited:
                    continue
                visited.add(above)
                yield above

    def settle(self) -> None:
        dirty = True
        while dirty:
            dirty = False
            for stick in self.sticks:
                while self.can_drop(stick):
                    stick.drop(self)
                    dirty = True

    def disintegratable_sticks(self) -> Iterable[Stick]:
        for stick in self.sticks:
            for supported in self.supporting(stick):
                if self.can_drop(supported, ignore={stick}):
                    break
            else:
                yield stick

def main():
    input_data = '\n'.join(line.rstrip() for line in stdin.read().splitlines())
    document = Document(input_data)

    document.settle()

    print(sum(1 for _ in document.disintegratable_sticks()))

if __name__ == '__main__':
    main()
