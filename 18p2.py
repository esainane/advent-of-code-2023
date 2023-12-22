#!/usr/bin/env python3

from collections import defaultdict
from itertools import chain
from sys import argv, stderr, stdin
from typing import Dict, Iterable, List, Tuple

from pyparsing import alphanums, delimitedList, nums, Group, Keyword, White, Word, ZeroOrMore

number = Word(nums)
hexnum = '0123456789abcdef'
direction = Keyword('U') | Keyword('D') | Keyword('L') | Keyword('R')
dig_list = Group(direction('wrong_direction') + number('wrong_distance') + '(#' + Word(hexnum, exact=5)('distance') + Word(hexnum, exact=1)('direction') + ')')
document = ZeroOrMore(dig_list)('edges')

def d(*args, **kwargs):
    #print(file=stderr, *args, **kwargs)
    pass

# Note that much of problem 18 is the construction of problem 10

class Direction(object):
    def __init__(self, dx: int, dy: int, straight_repr: str):
        self.dx = dx
        self.dy = dy
        self.straight_repr = straight_repr
        # A direction's test point is a point 45 degrees clockwise from the
        # direction.
        # This is used to determine which side of the direction is the
        # inside of the polygon.
        self.test_point = ((dx - dy) / 2, (dx + dy) / 2)

    def set_turn_mapping(self, mapping: Dict[str, 'Direction']):
        self.turn_mapping = mapping

    def set_opposite(self, opposite: 'Direction'):
        self.opposite = opposite
        opposite.opposite = self

    def __iter__(self) -> Iterable[int]:
        yield self.dx
        yield self.dy

    def __repr__(self):
        return f'Direction({self.dx}, {self.dy}, "{self.straight_repr}")'

north = Direction(0, -1, '|')
south = Direction(0, 1, '|')
east = Direction(1, 0, '-')
west = Direction(-1, 0, '-')

north.set_turn_mapping({'|': north, 'F': east, '7': west})
south.set_turn_mapping({'|': south, 'L': east, 'J': west})
east.set_turn_mapping({'-': east, '7': south, 'J': north})
west.set_turn_mapping({'-': west, 'F': south, 'L': north})

north.set_opposite(south)
east.set_opposite(west)


def cell_from_directions(d1, d2) -> str:
    '''
    Return a cell connected to two provided directions.
    '''
    if d1 == d2:
        return d1.straight_repr
    bend = set((d1, d2))
    if bend == set((north, east)):
        return 'L'
    elif bend == set((north, west)):
        return 'J'
    elif bend == set((south, east)):
        return 'F'
    elif bend == set((south, west)):
        return '7'
    else:
        raise ValueError(f'Unknown directions {d1}, {d2}')

def direction_from_dig_instruction(dig_dir: str) -> Direction:
    if dig_dir in '3U':
        return north
    elif dig_dir in '1D':
        return south
    elif dig_dir in '2L':
        return west
    elif dig_dir in '0R':
        return east
    else:
        raise ValueError(f'Unknown direction {dig_dir}')

cardinal_directions = (north, east, south, west)

def is_reflex(dir1, dir2):
    '''
    Determine whether two directions form a reflex angle.
    '''
    return dir1.dx * dir2.dy - dir1.dy * dir2.dx < 0

class Document(object):
    def __init__(self, input_data: str):
        self.data = document.parse_string(input_data, parse_all=True)

    def build_polygon(self):
        # Find the area of a many-edged polygon.
        # Note that each edge is built out of 1m x 1m squares.
        # The edges are extremely long, so we cannot build a grid and count
        # set squares.
        # Instead, we will work out where the true boundary coordinates are,
        # creating a polygon without further qualifications, and then
        # calculate the area of that polygon.

        # First, construct the real polygon.
        # We do this by effectively growing the length of each edge by 1m.
        # This is reduced by 1m for each incident reflex angle.
        # To determine whether an angle is a reflex angle, we need to know
        # the direction of the previous edge, and which way the inside of the
        # polygon is.
        # Fortunately, as each edge has a minimum length of 1, and always
        # travels in a cardinal direction, we can check which side of the edge
        # is the inside of the polygon by checking whether a point 0.5, 0.5
        # away from the start of an edge lies within the Polygon

        # Firstly, construct the basic polygon, which contains all ungrown
        # points.
        basic_coords = []
        x, y = 0, 0
        basic_coords.append((x, y))
        last_dir = direction_from_dig_instruction(self.data.edges[-1].direction).opposite
        for edge in self.data.edges:
            distance = int(edge.distance, base=16)
            direction = direction_from_dig_instruction(edge.direction)
            # Check that we don't have two straight lines in a row, as that
            # would mean even more edge cases
            assert(last_dir != direction)
            x += direction.dx * distance
            y += direction.dy * distance
            basic_coords.append((x, y))
            last_dir = direction

        # Determine which way around the polygon is.
        # We do this by checking whether the point 0.5, 0.5 away from the
        # start of the first edge is inside the polygon, relative to direction
        # the edge is travelling.
        # If the points were not presented in a clockwise order, we reverse
        # the basic polygon so that points are always presented in a clockwise
        # order.
        test_point = direction_from_dig_instruction(self.data.edges[0].direction).test_point
        clockwise_edges = self.data.edges[:]
        normalize_direction = lambda x: x
        if not self.trace_ray(test_point, basic_coords):
            clockwise_edges = clockwise_edges.reverse()
            normalize_direction = lambda x: x.opposite

        # Now, construct the real polygon.
        coordinates = []
        x, y = 0, 0
        coordinates.append((0,0))

        clockwise_edges.append(clockwise_edges[0])

        for i, edge in enumerate(clockwise_edges[:-1]):
            distance = int(edge.distance, base=16)
            last_dir = normalize_direction(direction_from_dig_instruction(clockwise_edges[i - 1].direction))
            direction = normalize_direction(direction_from_dig_instruction(edge.direction))
            next_dir = normalize_direction(direction_from_dig_instruction(clockwise_edges[i + 1].direction))

            # Grow the edge
            distance += 1

            # And shrink the edge for each reflex angle involved. This can
            # potentially mean an edge length of 0 in the real polygon (but
            # not the basic polygon we used for testing), which the shoelace
            # formula handles fine.

            # If the starting vertex is a reflex angle, shrink this edge
            if is_reflex(last_dir, direction):
                distance -= 1
            # If the ending vertex is a reflex angle, shrink this edge
            if is_reflex(direction, next_dir):
                distance -= 1

            x += direction.dx * distance
            y += direction.dy * distance
            coordinates.append((x, y))
            last_dir = direction

        # Check we have a closed polygon
        assert(coordinates[0] == coordinates[-1])

        self.coordinates = coordinates
    
    def trace_ray(self, point: Tuple[int, int], vertices: List[Tuple[int, int]]) -> bool:
        '''
        Test to see whether a point is contained within a polygon.
        '''
        # We do this by casting a ray from the point, and counting the number
        # of edges it intersects.
        # If the number of intersections is odd, the point is inside the
        # polygon.
        intersections = 0
        x, y = point
        for i in range(len(vertices) - 1):
            x1, y1 = vertices[i]
            x2, y2 = vertices[i + 1]
            if y1 == y2:
                # This edge is horizontal, so it can't intersect our ray
                continue
            elif y1 > y2:
                # Swap the points so that y1 < y2
                x1, x2 = x2, x1
                y1, y2 = y2, y1
            if y1 <= y < y2:
                # This edge is in the right y range to intersect our ray
                # Check whether it actually does
                x_intersect = x1 + (x2 - x1) * (y - y1) / (y2 - y1)
                if x_intersect > x:
                    # This edge does intersect our ray
                    intersections += 1
        return intersections % 2 == 1


    def area(self):
        coordinates = self.coordinates

        # Now, we need to find the area of this polygon.
        # We do this by applying the shoelace formula.

        area = 0
        for i in range(len(coordinates) - 1):
            x1, y1 = coordinates[i]
            x2, y2 = coordinates[i + 1]
            area += x1 * y2 - x2 * y1
        return area // 2

def main():
    input_data = '\n'.join(line.rstrip() for line in stdin.read().splitlines())
    document = Document(input_data)

    d(document.data)

    document.build_polygon()

    d(document.coordinates)

    print(document.area())

if __name__ == '__main__':
    main()
