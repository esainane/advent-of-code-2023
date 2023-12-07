#!/usr/bin/env python3

from collections import defaultdict
from enum import Enum
from functools import cmp_to_key
from sys import stdin

from pyparsing import Word, Group, ZeroOrMore

card_characters = "23456789TJQKA"

number = Word('0123456789')
entry = Group(Word(card_characters)('hand') + number('bid'))
document = ZeroOrMore(entry)

card_values = {card: value for value, card in enumerate(card_characters)}

Card = Enum('Card', card_characters)
HandType = Enum('HandType', 'HIGH_CARD PAIR TWO_PAIR THREE_OF_A_KIND FULL_HOUSE FOUR_OF_A_KIND FIVE_OF_A_KIND'.split())

class HandType(Enum):
    HIGH_CARD = 0
    PAIR = 1
    TWO_PAIR = 2
    THREE_OF_A_KIND = 3
    FULL_HOUSE = 4
    FOUR_OF_A_KIND = 5
    FIVE_OF_A_KIND = 6

class Hand(object):
    def __init__(self, cards: str, bid: int):
        self.cards = cards
        self.card_counts = defaultdict(int)
        self.bid = bid
        for card in cards:
            self.card_counts[card] += 1

    def type(self):
        '''
        Return the type of this hand.
        '''
        counts = sorted(self.card_counts.values())
        highest = counts[-1]
        if highest == 5:
            return HandType.FIVE_OF_A_KIND
        elif highest == 4:
            return HandType.FOUR_OF_A_KIND
        elif counts == [2, 3]:
            return HandType.FULL_HOUSE
        elif highest == 3:
            return HandType.THREE_OF_A_KIND
        elif counts[-2:] == [2, 2]:
            return HandType.TWO_PAIR
        elif highest == 2:
            return HandType.PAIR
        else:
            return HandType.HIGH_CARD

    def winnings(self):
        return self.bid * self.rank

class Document(object):
    def __init__(self, input_data: str):
        self.hands = [Hand(result.hand, int(result.bid)) for result in document.parse_string(input_data)]

    def update_ranks(self):
        '''
        Update the ranks of all hands. Hands are sorted first by type, then by
        the value of each card in their hand, in definition order.
        '''
        def comparator(l, r):
            # Sort first by type
            if l.type() != r.type():
                return l.type().value - r.type().value
            for lc, rc in zip(l.cards, r.cards):
                if lc != rc:
                    return card_values[lc] - card_values[rc]
            return 0
        s = sorted(self.hands, key=cmp_to_key(comparator))
        # Notify each hand of its new rank
        for i, hand in enumerate(s):
            hand.rank = i + 1
        self.hands = s

input_data = '\n'.join(line.rstrip() for line in stdin)
data = Document(input_data)
data.update_ranks()

# Print the winnings for each hand
#for hand in data.hands:
#    print(hand.cards, hand.bid, hand.type().name, hand.rank, hand.winnings())

# Print the sum total winnings
print(sum(hand.winnings() for hand in data.hands))
