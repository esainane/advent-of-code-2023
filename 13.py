#!/usr/bin/env python3

from collections import defaultdict
from itertools import chain
from sys import argv, stderr, stdin
from typing import Dict, Iterable, List, Tuple

def d(*args, **kwargs):
    print(file=stderr, *args, **kwargs)
    pass

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
        Find all the values of the patterns.
        '''
        for pattern in self.patterns:
            # Find a horizontal mirror
            mirror = find_mirror(pattern)
            if mirror is None:
                # Find a vertical mirror
                mirror = find_mirror('\n'.join(''.join(line) for line in zip(*pattern.split('\n'))))
                assert(mirror is not None)
                yield mirror
            else:
                # A mirror placed horizontally has 100 times the index value
                yield 100 * mirror

def main():
    input_data = '\n'.join(line.rstrip() for line in stdin)
    data = Document(input_data)


    # Print out the sum
    print(sum(data.find_all_pattern_values()))


if __name__ == '__main__':
    main()
