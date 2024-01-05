#!/usr/bin/env python3

from collections import defaultdict
import functools
from sys import argv, stderr, stdin
from typing import Iterable, List, Tuple

def d(*args, **kwargs):
    print(file=stderr, *args, **kwargs)
    pass

def triangle(n):
    return n * (n + 1) // 2

class Grid(object):
    def __init__(self, input_data: List[List[str]]):
        self.grid = input_data
        self.stride = len(self.grid[0]) + len(self.grid)
        self.last = {}

    def find_labelled_start(self) -> Tuple[int, int]:
        for y, row in enumerate(self.grid):
            for x, cell in enumerate(row):
                if cell == 'S':
                    return x, y
        raise ValueError('No starting position found')

    def count_reachable_plots(self, max_distance=64) -> int:
        x, y = self.find_labelled_start()

        plots_reachable_per_full_block = self._count_reachable_plots(x, y, self.stride)

        # Check that the grid is actually sparse, and that a stride is sufficient
        # to reach everything reachable in a block
        # This massively simplifies the algorithm if we can make this assumption
        assert(plots_reachable_per_full_block == self._count_reachable_plots(x, y, self.stride + 20))

        full_blocks = reachable_sum = 0

        # Calculate the number of blocks in each of the cardinal directions
        # from the starting position
        w, h = len(self.grid[0]), len(self.grid)

        # Simplifies a lot if we can make this assumption
        assert(w == h)

        def cardinal_ray(dist, s_x, s_y, name):
            nonlocal reachable_sum, full_blocks
            if dist < 0:
                return
            dlen = dist
            dlen //= w
            drem = dist - dlen * w

            outer_cells = self._count_reachable_plots(s_x, s_y, drem) if drem >= 0 else 0
            reachable_sum += outer_cells
            if dlen < 1:
                d('Outer ray', name, 'is too short to have an inner partial block or reach any full blocks; added', outer_cells, 'cells from outer block')
                return
            dlen -= 1
            drem += w
            inner_cells = self._count_reachable_plots(s_x, s_y, drem) if drem >= 0 else 0
            reachable_sum += inner_cells

            # We now have dlen full blocks to allocate. However, full blocks are not uniform - we
            # might have odd withs or heights and so cover a block with a different checkerboard
            # pattern, resulting in a diffrent number of cells!
            # To handle this, calculate the first full block, and then the second full block.
            # Extend these through multiplication to the number of full blocks we have.
            first_full_block_cells = self._count_reachable_plots(s_x, s_y, dist)
            second_full_block_cells = self._count_reachable_plots(s_x, s_y, dist - w)
            reachable_sum += first_full_block_cells * ((dlen + 1) // 2) + second_full_block_cells * (dlen // 2)
            #full_blocks += dlen
            d('Cardinal ray', name, 'added', outer_cells, 'cells from outer block, and', inner_cells, 'cells from inner block; added', ((dlen + 1) // 2), '/', (dlen // 2), 'full blocks (', first_full_block_cells, '/', second_full_block_cells, ')')
            self.last[name] = (outer_cells, inner_cells)

        cardinal_ray(max_distance - x - 1, w - 1, y, 'west')
        cardinal_ray(max_distance - (w - x), 0, y, 'east')
        cardinal_ray(max_distance - y - 1, x, h - 1, 'north')
        cardinal_ray(max_distance - (h - y), x, 0, 'south')

        d('Post cardinal rays: sum from partial blocks:', reachable_sum, '; full blocks:', full_blocks)

        # Add in the diagonal partial blocks and filled blocks
        def diagonal(dist, s_x, s_y, name):
            nonlocal reachable_sum, full_blocks
            if dist < 0:
                return
            dlen = dist
            dlen //= w
            drem = dist - dlen * w

            reachable_per_outer_cell = self._count_reachable_plots(s_x, s_y, drem) if drem >= 0 else 0
            dlen -= 1
            drem += w
            reachable_per_inner_cell = self._count_reachable_plots(s_x, s_y, drem) if drem >= 0 else 0

            reachable_sum += reachable_per_outer_cell * (dlen + 2)
            reachable_sum += reachable_per_inner_cell * (dlen + 1)

            # Similarly, full blocks are not necessarily uniform in the number of cells they have.
            # Calculate the first block (corner incident to center) and second block (one further out)
            # and extend these through multiplication to the number of full blocks we have.
            first_full_block_cells = self._count_reachable_plots(s_x, s_y, dist)
            second_full_block_cells = self._count_reachable_plots(s_x, s_y, dist - w)
            # As dlen increases, we add another layer of diagonal blocks to
            # the triangle, alternating which kind of block we add.
            # So the sequence goes: (1,0), (1,2), (4,2), (4,6), (9,6), (9,12), (16,12), (16,20)
            # The first term is a simple square, incrementing every second dlen.
            first_blocks_count = max(0, ((dlen+1)//2)*((dlen+1)//2))
            # Similarly, the second term is 2 * triangle(n//2): 2 + 4 + 6 + ...
            second_blocks_count = max(0, 2 * triangle(dlen//2))
            reachable_sum += first_full_block_cells * first_blocks_count + second_full_block_cells * second_blocks_count
            #added_full_blocks = (dlen * (dlen + 1) // 2)
            #d(name, 'ray: adding', added_full_blocks, 'full blocks; outer cells:', dlen + 2, 'inner cells:', dlen + 1, '; reachable per outer cell, inner cell:', reachable_per_outer_cell, reachable_per_inner_cell)
            #full_blocks += added_full_blocks
            self.last[name] = (reachable_per_outer_cell, reachable_per_inner_cell)
        diagonal(max_distance - x - y - 2, w - 1, h - 1, 'northwest')
        diagonal(max_distance - (w - x) - y - 1, 0, h - 1, 'northeast')
        diagonal(max_distance - x - (h - y) - 1, w - 1, 0, 'southwest')
        diagonal(max_distance - (w - x) - (h - y), 0, 0, 'southeast')

        d('Post diagonal quadrants: sum from partial blocks:', reachable_sum, '; full blocks:', full_blocks)

        reachable_sum += plots_reachable_per_full_block * full_blocks
        self.last['full'] = plots_reachable_per_full_block

        d('Reachable sum after adding', full_blocks, 'full blocks of', plots_reachable_per_full_block, ':', reachable_sum)

        # Finally, add in the center
        center_cells = self._count_reachable_plots(x, y, max_distance)
        reachable_sum += center_cells

        d('Reachable sum after adding', center_cells, 'cells from center:', reachable_sum)

        return reachable_sum


    @functools.cache
    def _count_reachable_plots_wrap(self, x, y, max_distance) -> int:
        exact_reachable = 0

        w, h = len(self.grid[0]), len(self.grid)

        # Now, do a breadth-first search to find all reachable cells
        visited = set()
        to_visit = [((x, y), max_distance)]
        while to_visit:
            pos, dist = to_visit.pop(0)
            x, y = pos
            if (x, y) in visited:
                continue
            visited.add((x, y))
            if dist % 2 == 0:
                exact_reachable += 1
            if dist == 0:
                continue
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                nx, ny = x + dx, y + dy
                if (nx, ny) in visited:
                    continue
                if self.grid[ny % h][nx % w] == '#':
                    continue
                to_visit.append(((nx, ny), dist - 1))

        assert(exact_reachable >= 0)
        return exact_reachable

    @functools.cache
    def _count_reachable_plots_wrap_items(self, x, y, max_distance) -> Iterable[Tuple[int, int]]:
        exact_reachable = 0

        w, h = len(self.grid[0]), len(self.grid)

        ret = set()

        # Now, do a breadth-first search to find all reachable cells
        visited = set()
        to_visit = [((x, y), max_distance)]
        while to_visit:
            pos, dist = to_visit.pop(0)
            x, y = pos
            if (x, y) in visited:
                continue
            visited.add((x, y))
            if dist % 2 == 0:
                ret.add((x, y))
            if dist == 0:
                continue
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                nx, ny = x + dx, y + dy
                if (nx, ny) in visited:
                    continue
                if self.grid[ny % h][nx % w] == '#':
                    continue
                to_visit.append(((nx, ny), dist - 1))

        assert(exact_reachable >= 0)
        return ret
    
    @functools.cache
    def _count_reachable_plots(self, x, y, max_distance) -> int:
        exact_reachable = 0

        # Now, do a breadth-first search to find all reachable cells
        visited = set()
        to_visit = [((x, y), max_distance)]
        while to_visit:
            pos, dist = to_visit.pop(0)
            x, y = pos
            if (x, y) in visited:
                continue
            visited.add((x, y))
            if dist % 2 == 0:
                exact_reachable += 1
            if dist == 0:
                continue
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                nx, ny = x + dx, y + dy
                if nx < 0 or nx >= len(self.grid[0]):
                    continue
                if ny < 0 or ny >= len(self.grid):
                    continue
                if (nx, ny) in visited:
                    continue
                if self.grid[ny][nx] == '#':
                    continue
                to_visit.append(((nx, ny), dist - 1))

        assert(exact_reachable >= 0)
        return exact_reachable

    def display(self):
        for row in self.grid:
            d(''.join(row))



def main():
    input_data = [[c for c in line.rstrip()] for line in stdin.read().splitlines()]
    grid = Grid(input_data)

    grid.display()

    print(grid.count_reachable_plots(26501365))

    grid.display()

from parameterized import parameterized
import unittest

sample_input = None
full_input = None

with open('21.sample.in', 'r') as f:
    sample_input = f.read()
with open('21.in', 'r') as f:
    full_input = f.read()

class Test(unittest.TestCase):
    @parameterized.expand([
        ( 6, 16 ),
        ( 10, 50 ),
        ( 50, 1594 ),
        ( 100, 6536 ),
        ( 500, 167004 ),
        #( 1000, 668697 ),
        #( 5000, 16733044 ),
    ])
    def test_reference_implementation(self, steps, expected):
        d('---')
        grid = Grid([[c for c in line.rstrip()] for line in sample_input.splitlines()])
        x, y = grid.find_labelled_start()
        actual = grid._count_reachable_plots_wrap(x, y, steps)
        if expected != actual:
            d('Answer off by', actual - expected)
        self.assertEqual(expected, actual)
        actual_items = len(grid._count_reachable_plots_wrap_items(x, y, steps))
        self.assertEqual(expected, actual_items)
    @parameterized.expand([
        ( 6, ),
        ( 10, ),
        ( 50, ),
        ( 100, ),
        ( 500, ),
    ])
    def test_item_reference_implementation(self, steps):
        d('---')
        grid = Grid([[c for c in line.rstrip()] for line in full_input.splitlines()])
        x, y = grid.find_labelled_start()
        expected = grid._count_reachable_plots_wrap(x, y, steps)
        actual = len(grid._count_reachable_plots_wrap_items(x, y, steps))
        self.assertEqual(expected, actual)

    def test_rays_100(self):
        steps = 100
        grid = Grid([[c for c in line.rstrip()] for line in full_input.splitlines()])
        x, y = grid.find_labelled_start()
        w, h = len(grid.grid[0]), len(grid.grid)
        plots = [v for v in grid._count_reachable_plots_wrap_items(x, y, steps)]

        expected_nw = len([(x,y) for (x,y) in plots if x<0 and y < 0])
        self.assertEqual(expected_nw, 0)

        expected_w = len([(x,y) for (x,y) in plots if x<0])
        self.assertEqual(expected_w, 546)

        expected_e = len([(x,y) for (x,y) in plots if x>=w])
        self.assertEqual(expected_e, 562)

        expected_n = len([(x,y) for (x,y) in plots if y<0])
        self.assertEqual(expected_n, 561)

        expected_s = len([(x,y) for (x,y) in plots if y>=h])
        self.assertEqual(expected_s, 553)

    def test_rays_500(self):
        steps = 500
        grid = Grid([[c for c in line.rstrip()] for line in full_input.splitlines()])
        x, y = grid.find_labelled_start()
        w, h = len(grid.grid[0]), len(grid.grid)
        d(w, h)
        plots = [v for v in grid._count_reachable_plots_wrap_items(x, y, steps)]
        grid.count_reachable_plots(steps)

        # block x -> block y -> count
        blocks = defaultdict(lambda : defaultdict(int))
        for (x,y) in plots:
            blocks[x // w][y // h] += 1

        blocks_x_offset = min(blocks.keys())
        blocks_y_offset = min(min(blocks[x].keys()) for x in blocks.keys())

        full = grid.last['full']
        ofull = 7523 # FIXME
        outer_w, inner_w = grid.last['west']
        outer_e, inner_e = grid.last['east']
        outer_n, inner_n = grid.last['north']
        outer_s, inner_s = grid.last['south']

        outer_nw, inner_nw = grid.last['northwest']
        outer_ne, inner_ne = grid.last['northeast']
        outer_sw, inner_sw = grid.last['southwest']
        outer_se, inner_se = grid.last['southeast']

        d(type(full), type(ofull))

        actual = [
            [       0,        0,        0,        0, outer_n,        0,        0,        0,       0 ],
            [       0,        0,        0, outer_nw, inner_n, outer_ne,        0,        0,       0 ],
            [       0,        0, outer_nw, inner_nw,    full, inner_ne, outer_ne,        0,       0 ],
            [       0, outer_nw, inner_nw,     full,   ofull,     full, inner_ne, outer_ne,       0 ],
            [ outer_w, inner_w,      full,    ofull,    full,    ofull,     full,  inner_e, outer_e ],
            [       0, outer_sw, inner_sw,     full,   ofull,     full, inner_se, outer_se,       0 ],
            [       0,        0, outer_sw, inner_sw,    full, inner_se, outer_se,        0,       0 ],
            [       0,        0,        0, outer_sw, inner_s, outer_se,        0,        0,       0 ],
            [       0,        0,        0,        0, outer_s,        0,        0,        0,       0 ],
        ]
        d('')
        d('Expected values:')
        for y, row in enumerate(actual):
            for x, actual_v in enumerate(row):
                expected = blocks[x + blocks_x_offset][y + blocks_y_offset]
                if x > 0:
                    d(",", end="")
                d(f'{expected:5}', end="")
            d('')
        d('')
        d('Actual values:')
        for y, row in enumerate(actual):
            for x, actual_v in enumerate(row):
                if x > 0:
                    d(",", end="")
                d(f'{actual_v:5}', end="")
            d('')

        for y, row in enumerate(actual):
            for x, actual_v in enumerate(row):
                expected = blocks[x + blocks_x_offset][y + blocks_y_offset]
                self.assertEqual(actual_v, expected, f'Block {x}, {y} expected {expected} got {actual_v}')

    @parameterized.expand([
        ( 6, ),
        ( 10, ),
        ( 50, ),
        ( 100, ),
        ( 500, ),
        ( 1000, ),
        #( 5000, ),
    ])
    def test_full_search(self, steps):
        d('---')
        grid = Grid([[c for c in line.rstrip()] for line in full_input.splitlines()])
        x, y = grid.find_labelled_start()
        expected = grid._count_reachable_plots_wrap(x, y, steps)
        actual = grid.count_reachable_plots(steps)
        if expected != actual:
            d('Answer off by', actual - expected)
        self.assertEqual(expected, actual)

if __name__ == '__main__':
    if len(argv) > 1 and argv[1] == '-t':
        # Add the test suite
        suite = unittest.TestLoader().loadTestsFromTestCase(Test)
        # Run them
        unittest.main(argv=[argv[0] + ' -t'] + argv[2:])
    else:
        main()
