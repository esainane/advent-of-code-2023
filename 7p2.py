#!/usr/bin/env python3

from collections import defaultdict
from enum import Enum
from functools import cmp_to_key
from sys import stdin

from pyparsing import Word, Group, ZeroOrMore

card_characters = "J23456789TQKA"

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
        self.jokers = self.card_counts['J']
        del self.card_counts['J']

    def type(self):
        '''
        Return the type of this hand.
        '''
        # Special case: No regular cards to consider
        if self.jokers == 5:
            return HandType.FIVE_OF_A_KIND

        # Get the various counts of regular cards
        counts = sorted(self.card_counts.values())
        highest = counts[-1] + self.jokers

        if highest == 5:
            return HandType.FIVE_OF_A_KIND
        if highest == 4:
            return HandType.FOUR_OF_A_KIND
        if counts == [2, 3]:
            return HandType.FULL_HOUSE
        # Note that if we had three jokers, we could always make four of a
        # kind, so we can have at most two jokers.
        # If we have two jokers, we can have at most one of any other card,
        # since two of any other card would have let us make four of a kind.
        # This means we can never make a full house with two jokers at this
        # point.
        if self.jokers == 1 and counts[-2:] == [2,2]:
            return HandType.FULL_HOUSE
        if highest == 3:
            return HandType.THREE_OF_A_KIND
        if counts[-2:] == [2, 2]:
            return HandType.TWO_PAIR
        # Similarly, if we had at least two jokers, we could always make
        # three of a kind, so we can have at most one joker at this point.
        if counts[-1] == 2 and self.jokers == 1:
            return HandType.TWO_PAIR
        if highest == 2:
            return HandType.PAIR
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
