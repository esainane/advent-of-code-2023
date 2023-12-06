#!/usr/bin/env python3

from functools import reduce
from math import ceil, floor
from sys import stdin
from typing import Iterable, List, Tuple

from pyparsing import Word, Keyword, Group, ZeroOrMore, ParseResults

# The grammar is as follows:

# document ::= times_list distance_list
# times_list ::= "Time:" (number ' ')+
# distances_list ::= "Distance:" (number ' ')+
# number ::= [0-9]+

number = Word('0123456789')
number_list = number + ZeroOrMore(number)
times_list = Keyword("Time:") + number_list('times')
distances_list = Keyword("Distance:") + number_list('distances')
document = times_list + distances_list

class Race(object):
    def __init__(self, time: int, distance: int):
        self.time = time
        self.distance = distance

    def viable_range(self) -> Tuple[float, float]:
        '''
        Returns an open interval (start, end) describing the values of s
        such s * (time - s) > distance.
        '''
        # We can rewrite the inequality as s^2 - ts + d < 0
        # Then we can use the quadratic formula to solve for s
        # s = (t +- sqrt(t^2 - 4d)) / 2
        # We care about both solutions, but need to clamp the resulting
        # interval to [0, t]
        # If t^2 - 4d < 0, then there are no solutions
        discriminant = self.time ** 2 - 4 * self.distance
        if discriminant < 0:
            return [0,0]

        # Otherwise, we can compute the solutions
        s1 = (self.time + discriminant ** 0.5) / 2
        s2 = (self.time - discriminant ** 0.5) / 2

        lower, upper = sorted((s1, s2))

        return (lower, upper)

    def viable_integer_range(self) -> Tuple[int, int]:
        '''
        Returns a half open interval [start, end) describing the values of s
        such that 0 <= s <= time and s * (time - s) > distance, and s is
        an integer.
        '''
        lower, upper = self.viable_range()

        # Avoid solutions that only equal, rather than beat, the current
        # record
        epsilon = 1e-10

        # clamp to the range [0, t]
        start = max(0, min(lower + epsilon, self.time))
        end = min(max(0, upper - epsilon), self.time)

        return (ceil(start), ceil(end))
    
    def viable_integer_count(self) -> int:
        '''
        Returns the number ways to beat the current record using integer
        splits of available time.
        '''
        start, end = self.viable_integer_range()
        if end <= start:
            return 0
        return end - start

class Document(object):
    def __init__(self, input_data):
        result = document.parse_string(input_data, parse_all=True)
        races = zip(result.times, result.distances)
        self.races = [Race(int(t), int(d)) for t,d in races]

input_data = '\n'.join(line.rstrip() for line in stdin)
data = Document(input_data)

# Print out the number of different ways we could win each race
#for r in data.races:
#    print(r.viable_range(), r.viable_integer_range(), r.viable_integer_count())

# Print out the product of the number of different ways we could win each race
print(reduce(lambda l,r: l*r, (r.viable_integer_count() for r in data.races)))
