#!/usr/bin/env python3

from collections import defaultdict
from itertools import chain
from sys import argv, stderr, stdin
from typing import Dict, Iterable, List, Tuple

def d(*args, **kwargs):
    #print(file=stderr, *args, **kwargs)
    pass

def hash(seq: str) -> int:
    '''
    Compute a hash value for a string.

    Each character is converted to an ordinal. In turn, each is added to the
    cumulative hash, multiplied by 17, then modulo 256.
    '''
    value = 0
    for i in seq:
        c = ord(i)
        value += c
        value *= 17
        value %= 256
    return value

def init_sequence(input_data: str) -> int:
    '''
    Compute the initial sequence for a given input.

    This is the sum of the hash values of each substring of the input.
    '''
    input_data = input_data.replace('\n', '').replace('\r', '')
    seqs = input_data.split(',')
    return sum(hash(s) for s in seqs)

def main():
    input_data = stdin.read()
    result = init_sequence(input_data)
    d(f"'{input_data}' -> {result}")
    print(result)

# Test suite

from parameterized import parameterized
import unittest

class Test(unittest.TestCase):
    @parameterized.expand([
        ('H', 200),
        ('HA', 153),
        ('HAS', 172),
        ('HASH', 52),
        ('rn=1', 30),
        ('cm-', 253),
        ('qp=3', 97),
        ('cm=2', 47),
        ('qp-', 14),
        ('pc=4', 180),
        ('ot=9', 9),
        ('ab=5', 197),
        ('pc-', 48),
        ('pc=6', 214),
        ('ot=7', 231),
    ])
    def test_hash(self, input_data, expected):
        d('---')
        result = hash(input_data)
        self.assertEqual(expected, result)
    
    def test_init_sequence(self):
        d('---')
        result = init_sequence('rn=1,cm-,qp=3,cm=2,qp-,pc=4,ot=9,ab=5,pc-,pc=6,ot=7')
        expected = 1320
        self.assertEqual(expected, result)

if __name__ == '__main__':
    if len(argv) > 1 and argv[1] == '-t':
        # Add the test suite
        suite = unittest.TestLoader().loadTestsFromTestCase(Test)
        # Run them
        unittest.main(argv=[argv[0] + ' -t'] + argv[2:])
    else:
        main()
