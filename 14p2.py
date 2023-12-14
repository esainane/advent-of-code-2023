#!/usr/bin/env python3

from collections import defaultdict
from itertools import chain
from sys import argv, stderr, stdin
from typing import Dict, Iterable, List, Tuple


def d(*args, **kwargs):
    print(file=stderr, *args, **kwargs)
    pass

identity = lambda x:x
def transpose(pattern: Iterable[str]) -> Iterable[str]:
    '''
    Transpose an iterable.
    '''
    return (''.join(line) for line in zip(*pattern))

def flip(row: str) -> str:
    '''
    Flip a string.
    '''
    return ''.join(c for c in reversed(row))

class Direction(object):
    def __init__(self, rows_mod, cells_mod):
        self.rows_mod = rows_mod
        self.cells_mod = cells_mod

    def apply_rows(self, rows):
        return self.rows_mod(rows)

    def apply_cells(self, cells):
        return self.cells_mod(cells)

west = Direction(identity, identity)
north = Direction(transpose, identity)
east = Direction(identity, flip)
south = Direction(transpose, flip)

class Document(object):
    def __init__(self, input_data: str):
        '''
        Store the current state of boulders.

        Each cell has one of three states:

        - '.' - empty
        - '#' - fixed boulder
        - 'O' - mobile boulder
        '''
        self.rows = tuple(input_data.split('\n'))

    def slide(self, row: Iterable[str]) -> str:
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
            empty = 0
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

    def slide_all(self, dir: Direction):
        '''
        Slide all mobile boulders to the start of their row.
        '''
        self.rows = tuple(r for r in dir.apply_rows(
            str(dir.apply_cells(self.slide(dir.apply_cells(row))))
        for row in dir.apply_rows(self.rows)))

    def do_cycle(self):
        '''
        Perform a single cycle of the document.
        '''
        self.slide_all(north)
        self.slide_all(west)
        self.slide_all(south)
        self.slide_all(east)

    def row_weight(self):
        '''
        Find the weight of each row.

        Each mobile boulder contributes its distance from the top edge.
        '''
        height = len(self.rows)
        return sum(height - i for i, row in enumerate(self.rows) for cell in row if cell == 'O')

    def __str__(self):
        return '\n'.join(self.rows)


def main():
    input_data = '\n'.join(line.rstrip() for line in stdin)
    # Transpose the input data, so we can work row by row
    data = Document(input_data)

    # Print out the document state before and after tilting
    d('Before:')
    d(data)
    cycle_state = {}
    target_iterations = 1000000000
    loop_length = target_iterations
    for i in range(target_iterations):
        if str(data) in cycle_state:
            d('Loop detected!')
            loop_length = i - cycle_state[str(data)]
            d(f'Loop length: {loop_length}')
            target_iterations -= i
            break
        cycle_state[str(data)] = i
        data.do_cycle()
    else:
        d('Reached end of cycles without finding a loop')
        target_iterations = 0
    target_iterations %= loop_length
    for i in range(target_iterations):
        data.do_cycle()
    d('After:')
    d(data)

    # Print out the sum
    print(data.row_weight())


if __name__ == '__main__':
    main()
