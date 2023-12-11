#!/usr/bin/env python3

from sys import stderr, stdin
from typing import Dict, Iterable, List, Tuple

def d(*args, **kwargs):
    #pass
    print(file=stderr, *args, **kwargs)

class Grid(object):
    def __init__(self, input_data: List[str]):
        self.cells = input_data
        # Find out which rows and columns are completely empty
        empty_rows = [i for i, row in enumerate(self.cells) if all(c == '.' for c in row)]
        empty_columns = [i for i in range(len(self.cells[0])) if all(row[i] == '.' for row in self.cells)]
        # Create a mapping from raw row/column to effective row/column number
        self.row_mapping = []
        row_offset = 0
        for i in range(len(self.cells)):
            if i in empty_rows:
                row_offset += 1
            self.row_mapping.append(i + row_offset)
        self.column_mapping = []
        column_offset = 0
        for i in range(len(self.cells[0])):
            if i in empty_columns:
                column_offset += 1
            self.column_mapping.append(i + column_offset)
        
        self.effective_width = len(self.cells[0]) + len(empty_columns)
        self.effective_height = len(self.cells) + len(empty_rows)
    
    def find_galaxies(self):
        '''
        Find all the galaxies in the grid.
        '''
        # Find all the stars
        stars = list(
            (self.column_mapping[x], self.row_mapping[y])
                for y, row in enumerate(self.cells)
                for x, cell in enumerate(row)
            if cell == '#'
        )
        return stars
    
    def find_complete_graph_lengths(self):
        '''
        Find the sum length of the complete graph.
        '''
        galaxies = self.find_galaxies()
        # Find all the edges
        for i, galaxy in enumerate(galaxies):
            for other_galaxy in galaxies[i:]:
                # Find taxicab distance between these points
                yield abs(galaxy[0] - other_galaxy[0]) + abs(galaxy[1] - other_galaxy[1])


input_data = list(line.rstrip() for line in stdin)
data = Grid(input_data)

# Print out the sum of all the edge lengths
print(sum(data.find_complete_graph_lengths()))
