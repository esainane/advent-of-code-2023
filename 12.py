#!/usr/bin/env python3

from collections import defaultdict
from itertools import chain
from sys import argv, stderr, stdin
from typing import Dict, Iterable, List, Tuple

from pyparsing import alphanums, delimitedList, Group, Keyword, White, Word, ZeroOrMore

number = Word('0123456789')
number_list = delimitedList(number)
springs = Word('.?#')
spring_list = Group(springs('springs') + number_list('group_list'))
document = ZeroOrMore(spring_list)('readings')

def d(*args, **kwargs):
    pass
    #print(file=stderr, *args, **kwargs)

class CachingPermuter(object):
    def __init__(self, input_data: List[str]):
        results = document.parse_string(input_data, parse_all=True)
        self.lines = ((
            self.line_setup(r.springs),
            tuple(int(v) for v in chain((0,), r.group_list))
        ) for r in results)
        # Maintain a cache:
        #  remaining line -> remaining groups required -> permutation_count
        self.cache = defaultdict(dict)

    def line_setup(self, springs: str) -> str:
        '''
        Transform an input line into a string containing all necessary
        non-group state.

        This contains the previous character, the current character, and the
        rest of the line.

        Remove all trailing and preceding empty space, to simplify the input.

        Prepend a single preceding empty space to the start of the string, to
        indicate that we do not necessarily need to start a group immediately.
        '''
        return '.' + springs.strip('.')

    def find_all_permutation_counts(self) -> Iterable[int]:
        '''
        Step through our list of input lines, and find all permutations.
        '''
        for springs, group_list in self.lines:
            # Find the number of permutations for this line
            result = self.find_permutation(springs, group_list)
            yield result

    def find_permutation(self, springs: str, group_list: Iterable[int], depth=0) -> int:
        '''
        Find the number of permutations for this line.

        Keep track of subproblems we've already solved in self.cache.
        '''
        # Normalize args: Strip off any preceding 0s
        group_list = tuple(int(v) for v in group_list)
        # Cache hit: return the cached result
        if group_list in self.cache[springs]:
            result = self.cache[springs][group_list]
            d(f'{" " * depth}Cache hit: "{springs}" {group_list} -> {result}')
            return result
        result = self._find_permutation(springs, group_list, depth=depth)
        # Cache the result
        self.cache[springs][group_list] = result
        return result

    def _find_permutation(self, state: str, group_list: List[int], depth=0) -> int:
        '''
        Find the number of permutations for this line.
        '''
        prev_char, springs = state[0], state[1:]
        groups_done = not group_list or group_list == (0,)
        # Base case: If we have no more springs or groups that need matching,
        # we're done (with exactly the one trivial solution)
        if not springs and groups_done:
            d(f'{" " * depth}{prev_char}        "" into {group_list}: 1 total combinations ({not springs}, {groups_done})')
            return 1
        # Base case: If we're out of springs, but we have nonempty groups left
        # to match, there are no solutions
        if not springs and not groups_done:
            d(f'{" " * depth}{prev_char}        "" into {group_list}: 0 total combinations ({not springs}, {groups_done})')
            return 0
        # Otherwise, pop off the head and recurse
        head, tail = springs[0], springs[1:]
        result = 0
        # If the head isn't (or might not be) a spring, explore the case
        if head in '.?':
            # A non-spring is valid here if there are no more springs left to
            # match in the current group
            if groups_done or group_list[0] == 0:
                as_empty = self.find_permutation('.' + tail, group_list, depth=depth+1)
                d(f'{" " * depth}{prev_char} <{head}>(.) "{tail}" into {group_list}: {as_empty} combinations')
                result += as_empty
        # If the head is (or could be) a spring, explore the case
        if head in '#?':
            # If there are no more springs left to match in the current group,
            # and the previous character was not a spring, close the old group
            if prev_char == '.':
                while group_list and group_list[0] == 0:
                    group_list = group_list[1:]
            # A spring is valid here if there are springs left to match in the
            # current group
            if group_list and group_list[0] > 0:
                group_list = (group_list[0] - 1,) + group_list[1:]
                as_spring = self.find_permutation('#' + tail, group_list, depth=depth+1)
                d(f'{" " * depth}{prev_char} <{head}>(#) "{tail}" into {group_list}: {as_spring} combinations')
                result += as_spring
        d(f'{" " * depth}{prev_char} <{head}>    "{tail}" into {group_list}: {result} total combinations')
        return result

def main():
    input_data = '\n'.join(line.rstrip() for line in stdin)
    data = CachingPermuter(input_data)

    # Print out the sum
    print(sum(data.find_all_permutation_counts()))

# Test suite

from parameterized import parameterized
import unittest

class Test(unittest.TestCase):
    @parameterized.expand([
        ('???? 2,1', 1),
        ('????? 2,1', 3),
        ('?????? 2,1', 6),
        ('??????? 2,1', 10),
        ('#.#.### 1,1,3', 1),
        ('.??..??...?##. 1,1,3', 4),
        ('?#?#?#?#?#?#?#? 1,3,1,6', 1),
        ('????.#...#... 4,1,1', 1),
        ('????.######..#####. 1,6,5', 4),
        ('?###???????? 3,2,1', 10),
    ])
    def test_permutations(self, input_data, expected):
        d('---')
        data = CachingPermuter(input_data)
        result = data.find_all_permutation_counts()
        self.assertEqual(expected, sum(result))

if __name__ == '__main__':
    if len(argv) > 1 and argv[1] == '-t':
        # Add the test suite
        suite = unittest.TestLoader().loadTestsFromTestCase(Test)
        # Run them
        unittest.main(argv=[argv[0] + ' -t'] + argv[2:])
    else:
        main()
