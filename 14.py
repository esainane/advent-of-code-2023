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

class Document(object):
    def __init__(self, input_data: str):
        '''
        Store the current state of boulders.

        Each cell has one of three states:

        - '.' - empty
        - '#' - fixed boulder
        - 'O' - mobile boulder
        '''
        self.rows = input_data.split('\n')

    def slide(self, row: str):
        '''
        Slide all mobile boulders to the start of their row.

        A boulder stops when it hits another boulder or the edge of the grid.
        '''
        result = ''
        # Count the number of empty spaces and mobile boulders.
        # Once we find a fixed boulder, commit the number of mobile boulders
        # to the left side, and empty spaces now fill the remainder.
        mobile = 0
        empty = 0
        def commit():
            nonlocal result, mobile, empty
            result += 'O' * mobile
            result += '.' * empty
            mobile = 0
            empty =0
        for cell in row:
            if cell == 'O':
                mobile += 1
            elif cell == '.':
                empty += 1
            elif cell == '#':
                commit()
                result += '#'
        commit()
        return result

    def slide_all(self):
        '''
        Slide all mobile boulders to the start of their row.
        '''
        self.rows = [self.slide(row) for row in self.rows]

    def row_weight(self):
        '''
        Find the weight of each row.

        Each mobile boulder contributes its distance from the right edge.
        '''
        length = len(self.rows[0])
        return sum(length - i for row in self.rows for i, cell in enumerate(row) if cell == 'O')

    def __str__(self):
        return '\n'.join(self.rows)


def main():
    input_data = '\n'.join(line.rstrip() for line in stdin)
    # Transpose the input data, so we can work row by row
    input_data = flip(input_data)
    data = Document(input_data)

    # Print out the document state before and after tilting
    d('Before:')
    d(data)
    data.slide_all()
    d('After:')
    d(data)

    # Print out the sum
    print(data.row_weight())


if __name__ == '__main__':
    main()
