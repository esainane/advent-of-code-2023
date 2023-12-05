#!/usr/bin/env python3

from collections import defaultdict
from sys import stdin
from typing import List

# Make use of pyparsing to cleanly handle all the input boilerplate

from pyparsing import Word, alphas, delimitedList, Keyword, Optional, Group, ZeroOrMore, ParseResults, White

card_id = Word('0123456789')
number_list = Group(delimitedList(Word('0123456789'), delim=White(' ')))
scratch_line = Keyword("Card") + card_id('id') + ':' + number_list('winning_numbers') + "|" + number_list('our_numbers')

copy_counter = defaultdict(lambda : 1)

class Card(object):
    def __init__(self, input_line):
        result = scratch_line.parse_string(input_line, parse_all=True)
        self.card_id = int(result.id)
        self.winning_numbers = result.winning_numbers
        self.our_numbers = result.our_numbers
        #print(self.card_id, self.winning_numbers, self.our_numbers)

        # We get bonus copies of the next cards, to a depth equal to the
        # number of matching numbers, to an amount equal to the number of
        # copies of this card we have
        copies = copy_counter[self.card_id]
        bonus_cards = len(self.our_winning_numbers())
        for x in range(bonus_cards):
            copy_counter[self.card_id + x + 1] += copies

    def our_winning_numbers(self):
        '''
        Return the set of our numbers that are also winning numbers.
        '''
        return set(self.our_numbers).intersection(self.winning_numbers)

    def value(self):
        '''
        Return the value of this card.

        The value of a card is 1 after the first matching number, and doubles
        for each additional matching number. A card without any matching
        numbers has a value of 0.
        '''
        amount = len(self.our_winning_numbers())
        return 2 ** (amount - 1) if amount else 0

cards = [Card(line.rstrip()) for line in stdin]
print(sum(copy_counter[card.card_id] for card in cards))