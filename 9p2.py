#!/usr/bin/env python3

from collections import defaultdict
import heapq
from itertools import chain, cycle
from functools import reduce
from sys import stdin
from typing import List

from pyparsing import alphanums, delimitedList, Group, Keyword, White, Word, ZeroOrMore

number = Word('-0123456789')
number_list = Group(delimitedList(number, delim=White(' ')))
document = ZeroOrMore(number_list)('readings')

class Document(object):
    def __init__(self, input_data: str):
        data = document.parse_string(input_data, parse_all=True)
        self.readings = [[int(v) for v in reversed(r)] for r in data.readings]
    
    def predict_next(self, seq: List[int]) -> int:
        '''
        Predict the next number in the sequence.
        '''
        # Base case: If they're all zero, predict zero
        if all(v == 0 for v in seq):
            return 0
        # Otherwise, predict the next diff and use that with our last value
        # Calculate a sequence of difference between each reading
        diffs = [r2 - r1 for r1, r2 in zip(seq, seq[1:])]
        # Predict the next element in our derivative
        predicted_diff = self.predict_next(diffs)
        # And apply that to our original sequence
        #print(f'{seq}: {predicted_diff + seq[-1]}')
        return predicted_diff + seq[-1]

input_data = '\n'.join(line.rstrip() for line in stdin)
data = Document(input_data)

# Print the sum of all the predicted next values
print(sum(data.predict_next(r) for r in data.readings))
