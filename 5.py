#!/usr/bin/env python3

from collections import defaultdict
from sys import stdin
from typing import Iterable, List

from pyparsing import Word, alphas, delimitedList, Keyword, Optional, Group, ZeroOrMore, ParseResults, White

# The grammar is as follows:

# almanac ::= "seeds:" number_list '\n\n' named_maps
# number_list ::= number (' ' number)*
# named_maps ::= named_map+
# named_map ::= source '-to-' target "map:" range_lists
# range_lists ::= range_list+
# range_list ::= number number number ('\n' number number number)*
# number ::= [0-9]+ 

number = Word('0123456789')
number_list = Group(delimitedList(number, delim=White(' ')))
range_list = Group(number('target_start') + number('source_start') + number('length'))
range_lists = range_list + ZeroOrMore(range_list)
named_map = Group(Word(alphas)('source') + '-to-' + Word(alphas)('target') + "map:" + range_lists('mappings'))
named_maps = named_map + ZeroOrMore(named_map)
almanac = Keyword("seeds") + ":" + number_list('seeds') + named_maps('maps')

class Segment(object):
    '''
    A segment represents a half-open interval [start, end).

    A SegmentTree always has concrete instances of SegmentLeaf and SegmentNode,
    but a user may supply a list of base Segments to construct the tree from.
    '''
    def __init__(self, start: int, end: int, userdata=None):
        self.start = start
        self.end = end
        self.userdata = userdata

    def __repr__(self):
        if not self.userdata:
            return f"Segment({self.start}, {self.end})"
        return f"Segment({self.start}, {self.end}, {self.userdata})"

    def __eq__(self, other):
        return self.start == other.start and self.end == other.end

    def __hash__(self):
        return hash((self.start, self.end))

    def query_overlap(self, start: int, end: int) -> Iterable:
        '''
        Return all segments that overlap the given interval.
        '''
        raise NotImplementedError

    def query_contained(self, start: int, end: int, allow_none=False) -> Iterable:
        '''
        Return all segments that are fully contained in the given interval.
        '''
        raise NotImplementedError

class SegmentLeaf(Segment):
    '''
    A segment leaf is a leaf node in a segment tree.
    '''
    def __init__(self, start: int, end: int, userdata=None):
        super().__init__(start, end, userdata)

    def __repr__(self):
        if not self.userdata:
            return f"SegmentLeaf({self.start}, {self.end})"
        return f"SegmentLeaf({self.start}, {self.end}, {self.userdata})"

    def query_overlap(self, start: int, end: int) -> Iterable[Segment]:
        '''
        Return all segments that overlap the given interval.
        '''
        if self.start < end and self.end > start and self.userdata is not None:
            yield self

    def query_contained(self, start: int, end: int, allow_none=False) -> Iterable:
        if self.start >= start and self.end <= end and (allow_none or self.userdata is not None):
            yield self

class SegmentNode(Segment):
    '''
    A segment node is a non-leaf node in a segment tree.
    '''
    def __init__(self, left: Segment, right: Segment):
        super().__init__(left.start, right.end)
        self.left = left
        self.right = right

    def __repr__(self):
        return f"SegmentNode[{self.start}, {self.end}]({self.left}, {self.right})"

    def __str__(self):
        return f"[{self.start}, {self.end}]({self.left}, {self.right})"

    def query_overlap(self, start: int, end: int) -> Iterable[Segment]:
        '''
        Return all segments that overlap the given interval.
        '''
        for n in (self.left, self.right):
            if n.start < end and n.end > start:
                yield from n.query_overlap(start, end)

    def query_contained(self, start: int, end: int, allow_none=False) -> Iterable[Segment]:
        '''
        Return all segments that are fully contained in the given interval.
        '''
        for n in (self.left, self.right):
            # Note: Still traversing nodes that merely overlap, as child nodes
            # may be more specific
            if n.start < end and n.end > start:
                yield from n.query_contained(start, end, allow_none)


class SegmentTree(object):
    '''
    A segment tree is a tree data structure for storing intervals, or segments.

    This allows for efficient queries of all segments that overlap a given
    interval, or all segments that are fully contained in a given interval.

    Very space efficient for sparse representations.
    '''
    def __init__(self, segments: List[Segment]):
        '''
        Construct a new segment tree for a list of segments.

        All segments should have non-None userdata to distinguish empty ranges.

        All endpoints in segments are sorted to obtain a list of unique
        endpoints, which are then used to construct the tree.

        The tree is constructed by recursively splitting the list of endpoints
        into two halves, and then constructing a tree for each half. The
        endpoints are then used to construct the tree's value, which is the
        number of segments that cover the interval between the start and end
        endpoints.
        '''
        # Sort and uniquify endpoints
        endpoints = sorted(set([s.start for s in segments] + [s.end for s in segments]))

        # Construct the tree
        self.root = self._construct(endpoints)

        # Apply user supplied values to leaves of the constructed tree
        for segment in segments:
            found = False
            for leaf in self.root.query_contained(segment.start, segment.end, allow_none=True):
                leaf.userdata = segment.userdata
                found = True
            if not found:
                print('Could not find corresponding leaf node for', segment)
                print('Tree contents:', self.root)
                raise RuntimeError(f'Could not find corresponding leaf node for [{segment.start}, {segment.end}) after tree construction')

    def _construct(self, endpoints: List[int]):
        '''
        Construct a new segment tree for a list of endpoints.
        '''
        # Base case: not enough endpoints
        if len(endpoints) <= 1:
            return None

        # Base case: two endpoints
        if len(endpoints) == 2:
            return SegmentLeaf(endpoints[0], endpoints[1])

        # Recursively construct subtrees
        mid = len(endpoints) // 2
        left = self._construct(endpoints[:mid + 1])
        right = self._construct(endpoints[mid:])

        return SegmentNode(left, right)

    def query_overlap(self, start: int, end: int) -> Iterable[Segment]:
        '''
        Return all segments that overlap the given interval.
        '''
        yield from self.root.query_overlap(start, end)

    def query_point(self, point: int) -> Iterable[Segment]:
        '''
        Return all segments that cover the given point.
        '''
        yield from self.root.query_overlap(point, point + 1)

    def query_contained(self, start: int, end: int) -> Iterable[Segment]:
        '''
        Return all segments that are fully contained in the given interval.
        '''
        yield from self.root.query_contained(start, end)

class AlmanacVertex(object):
    '''
    Helper class to represent implicit vertices in the almanac graph.
    '''
    def __init__(self, kind, id):
        self.kind = kind
        self.id = id

    def __repr__(self):
        return f'AlmanacVertex({self.kind}, {self.id})'

    def __str__(self):
        return f'{self.kind} {self.id}'

    def adjacent_vertices(self, almanac):
        out_edges = almanac.out_edges[self.kind]
        for target_kind in out_edges.keys():
            explicit = False
            for segment in out_edges[target_kind].query_point(self.id):
                # If we're contained in any ranges, use those
                source_start = segment.start
                target_start = segment.userdata[0]
                other_id = self.id - source_start + target_start
                yield AlmanacVertex(target_kind, other_id)
                explicit = True
            if not explicit:
                # Otherwise, an unmapped vertex ID just maps to itself
                yield AlmanacVertex(target_kind, self.id)


class Almanac(object):
    def __init__(self, input_data):
        result = almanac.parse_string(input_data, parse_all=True)
        self.seeds = [int(s) for s in result.seeds]
        # Source kind -> Target kind -> segment tree of ranges
        self.out_edges = defaultdict(lambda: {})
        for m in result.maps:
            st = SegmentTree([
                Segment(
                    int(r.source_start),
                    int(r.source_start) + int(r.length),
                    (int(r.target_start), int(r.length), m.target)
                ) for r in m.mappings
            ])
            self.out_edges[m.source][m.target] = st

    def search(self, sources: List[AlmanacVertex], f=lambda: False, visited=set()):
        '''
        Search for vertices accepted by f reachable from provided sources
        '''
        to_visit = [[v] for v in sources]
        while to_visit:
            path = to_visit.pop()
            n, *tail = path
            if n in visited:
                continue
            if f(n):
                yield n
            visited.add(n)
            for adj in n.adjacent_vertices(self):
                to_visit.append([adj, *path])

# Parse all input data
input_data = '\n'.join(line.rstrip() for line in stdin)
data = Almanac(input_data)
# Find all locations reachable from almanac seeds
reachable_locations = list(data.search(
    [AlmanacVertex('seed', s) for s in data.seeds],
    lambda v: v.kind == 'location'
))
# Print the ID of the lowest reachable location
print(min(reachable_locations, key=lambda v: v.id).id)
