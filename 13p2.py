#!/usr/bin/env python3

from collections import defaultdict
from itertools import chain
from sys import argv, stderr, stdin
from typing import Dict, Iterable, List, Tuple


def d(*args, **kwargs):
    print(file=stderr, *args, **kwargs)
    pass

def flip(pattern: str) -> str:
    '''
    Transpose a pattern over its newlines.
    '''
    return '\n'.join(''.join(line) for line in zip(*pattern.split('\n')))

def line_deltas(l: str, r: str) -> int:
    '''
    Find the number of different characters between two strings.
    '''
    return sum(1 for lc, rc in zip(l, r) if lc != rc)

def find_smudged_mirrors(pattern: str) -> int | None:
    '''
    Find a horizontally placed mirror within a pattern.

    We search for an index between where lines diverging from this index
    match. However, we tolerate the first non-matching character found in
    a pattern.

    No search for vertically placed mirrors is performed.
    '''
    d(f'Trying to find a new mirror in:\n{pattern}')
    lines = pattern.split('\n')
    for index, (upper, lower) in enumerate(zip(lines, lines[1:])):
        delta = 0
        ok = True
        for upper2, lower2 in zip(reversed(lines[:index + 1]), lines[index + 1:]):
            delta_this_line = line_deltas(upper2, lower2)
            delta += delta_this_line
            if delta > 1:
                ok = False
                break
        if not ok:
            continue
        if delta != 1:
            continue
        d(f'Found a new mirror (fixing one smudge) at {index + 1}')
        yield index + 1

def find_mirror(pattern: str) -> int | None:
    '''
    Find a horizontally placed mirror within a pattern.

    We search for an index between two lines where the pattern is the same,
    then verify other lines also match.

    No search for vertically placed mirrors is performed.
    '''
    d(f'Trying to find a mirror in:\n{pattern}')
    lines = pattern.split('\n')
    for index, (upper, lower) in enumerate(zip(lines, lines[1:])):
        if upper == lower:
            # Found a potential mirror
            # Check that all other lines match
            if all(upper2 == lower2 for upper2, lower2 in zip(reversed(lines[:index]), lines[index + 2:])):
                d(f'Found a mirror at {index}')
                return index + 1
            d(f'No mirror at index {index}')
            for upper2, lower2 in zip(reversed(lines[:index]), lines[index + 2:]):
                if upper2 != lower2:
                    d(f'  mismatch was\n    {upper2}\n  !=\n    {lower2}')
                    break
    return None


class Document(object):
    def __init__(self, input_data: str):
        self.patterns = input_data.split('\n\n')

    def find_all_pattern_values(self) -> Iterable[int]:
        '''
        Find each first smudged mirror that doesn't have the index of the
        clean mirror, and return its value.
        '''
        for pattern in self.patterns:
            og_index = find_mirror(pattern)
            if og_index is None:
                og_index = find_mirror(flip(pattern))
            else:
                og_index = og_index * 100
            done = False
            for index in find_smudged_mirrors(pattern):
                if index * 100 == og_index:
                    continue
                yield index * 100
                if done:
                    d(f'Found alterate index: {index * 100}')
                done = True
                # break
            # if done:
                # continue
            for index in find_smudged_mirrors(flip(pattern)):
                if index == og_index:
                    continue
                yield index
                if done:
                    d(f'Found alterate index: {index}')
                done = True

def main():
    input_data = '\n'.join(line.rstrip() for line in stdin)
    data = Document(input_data)

    # Print out the sum
    print(sum(data.find_all_pattern_values()))


if __name__ == '__main__':
    main()
