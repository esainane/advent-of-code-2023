#!/usr/bin/env python3

from sys import stdin
from typing import Any, Set

from pyparsing import alphanums, nums, Group, Iterable, Literal, OneOrMore, ParseResults, Tuple, Word


def d(*args, **kwargs):
    #print(file=stderr, *args, **kwargs)
    pass

number = Word(nums)
name = Word(alphanums)
comparator = Literal('=') | Literal('>') | Literal('<')
property_letter = Literal('x') | Literal('m') | Literal('a') | Literal('s')
property = property_letter

conditional_rule = property('property') + comparator('comparator') + number('value') + ':' + name('destination') + ','
rule = name('name') + '{' + OneOrMore(Group(conditional_rule))('conditionals') + (name)('fallback') + '}'

part = Literal('{x=') + number('x') + ',m=' + number('m') + ',a=' + number('a') + ',s=' + number('s') + '}'

document = OneOrMore(Group(rule))('rules') + OneOrMore(Group(part))('parts')

def property_to_index(property: str) -> int:
    return 'xmas'.index(property)

def update(t: Tuple, i: int, v):
    result = t[:i] + (v,) + t[i + 1:]
    assert(len(result) == len(t))
    return result

class Comparator(object):
    def __init__(self, comparator: str):
        self.comparator = comparator

    def __repr__(self):
        return f'<Comparator {self.comparator}>'

    def __call__(self, p, v):
        raise NotImplementedError()

    def multi_split(self, part: 'PartRange') -> Iterable['PartRange']:
        '''
        Split a part range into multiple parts based on this comparator.
        '''
        raise NotImplementedError()

class Equals(Comparator):
    def __init__(self):
        super().__init__('=')

    def __call__(self, p, v):
        return p == v

    def multi_split(self, part: 'PartRange', property_index: int, property_value: int, active_location: str) -> Iterable['PartRange']:
        start, end = part.properties[property_index]
        # If the part range is fully contained in the conditional, return our
        # destination
        if start <= property_value < end:
            yield PartRange(update(part.properties, property_index, (property_value, property_value + 1)), active_location)
        # If there is a range before our active region, return it with no
        # active location
        if start < property_value:
            yield PartRange(update(part.properties, property_index, (start, min(property_value, end))))
        # If there is a range after our active region, return it with no active location
        if property_value + 1 < end:
            yield PartRange(update(part.properties, property_index, (max(start, property_value + 1), end)))


class LessThan(Comparator):
    def __init__(self):
        super().__init__('<')

    def __call__(self, p, v):
        return p < v

    def multi_split(self, part: 'PartRange', property_index: int, property_value: int, active_location: str) -> Iterable['PartRange']:
        range = part.properties[property_index]
        start, end = range
        # If the part range is below our activating value, return it with
        # the active destination
        if start < property_value:
            yield PartRange(update(part.properties, property_index, (start, min(end, property_value))), active_location)
        # If there is a range after our activating value, returning it with
        # no active location
        if property_value < end:
            yield PartRange(update(part.properties, property_index, (max(property_value, start), end)))

class GreaterThan(Comparator):
    def __init__(self):
        super().__init__('>')

    def __call__(self, p, v):
        return p > v

    def multi_split(self, part: 'PartRange', property_index: int, property_value: int, active_location: str) -> Iterable['PartRange']:
        start, end = part.properties[property_index]
        # If the part range is above our activating value, return it with the
        # active destination
        if property_value + 1 < end:
            yield PartRange(update(part.properties, property_index, (max(property_value + 1, start), end)), active_location)
        if start < property_value + 1:
            yield PartRange(update(part.properties, property_index, (start, min(property_value + 1, end))))

equals = Equals()
less_than = LessThan()
greater_than = GreaterThan()

def comparator_str_to_func(comparator: str):
    if comparator == '=':
        return equals
    if comparator == '<':
        return less_than
    if comparator == '>':
        return greater_than

class Part(object):
    def __init__(self, part: ParseResults):
        d(part)
        self.properties = {
            'x': int(part.x),
            'm': int(part.m),
            'a': int(part.a),
            's': int(part.s)
        }

    def rated_value(self):
        return sum(self.properties.values())

class Conditional(object):
    def __init__(self, conditional: ParseResults):
        self.property = conditional.property
        self.property_index = property_to_index(self.property)
        self.comparator = comparator_str_to_func(conditional.comparator)
        self.value = int(conditional.value)
        self.destination = conditional.destination

    def test(self, part) -> bool:
        return self.comparator(part.properties[self.property], self.value)

    def multi_split(self, part: 'PartRange') -> Iterable[Part]:
        '''
        Split a part range into multiple parts based on our conditional.
        '''
        yield from self.comparator.multi_split(part, self.property_index, self.value, self.destination)

    def __repr__(self):
        return f'<Conditional {self.property}, {self.comparator}, {self.value}, {self.destination}>'

Range = Tuple[int, int]

class PartRange(object):
    def __init__(self, properties: Tuple[Range, Range, Range, Range], location: str | None = None):
        '''
        Stores half-open ranges for all four properties,
        and the current location of the parts represented by this range.
        '''
        self.properties = properties
        assert(len(properties) == 4)
        for p in properties:
            assert(len(p) == 2)
        self.location = location

    def combinations(self):
        result = 1
        for start, end in self.properties:
            result *= end - start
        return result

class Rule(object):
    def __init__(self, rule: ParseResults):
        d(rule)
        self.name = rule.name
        self.conditionals = conditionals = []
        for conditional in rule.conditionals:
            conditionals.append(Conditional(conditional))
        self.fallback = rule.fallback

    def process(self, part: Part) -> str:
        for conditional in self.conditionals:
            if conditional.test(part):
                return conditional.destination
        return self.fallback

    def multi_process(self, part: PartRange) -> Iterable[PartRange]:
        '''
        Process a part range with this rule, and return the resulting part
        ranges.
        '''
        part_ranges = [part,]
        for conditional in self.conditionals:
            next_part_ranges = []
            for part in part_ranges:
                for result in conditional.multi_split(part):
                    if result.location is not None:
                        yield result
                    else:
                        next_part_ranges.append(result)
            part_ranges = next_part_ranges
        for result in next_part_ranges:
            result.location = self.fallback
            yield result

    def __repr__(self):
        return f'Rule({self.name}, {self.conditionals}, {self.fallback})'

class Document(object):
    def __init__(self, input_data: str):
        self.spec = document.parse_string(input_data)
        self.rules = rules = {}
        for rule in self.spec.rules:
            r = Rule(rule)
            rules[r.name] = r
        self.parts = parts = []
        for part in self.spec.parts:
            parts.append(Part(part))

    def classify(self, part: Part, start: str='in', end: Set[str]={'A', 'R'}) -> str:
        '''
        Classify a part, starting from the provided state, and ending in the
        provided set of states.
        '''
        current = start
        while current not in end:
            current = self.rules[current].process(part)
        return current

    def multi_classify(self, part: PartRange, start: str='in', end: Set[str]={'A', 'R'}) -> Iterable[PartRange]:
        '''
        Classify all possible parts within the provided ranges. Parts will be
        returned as they reach end states.
        '''
        ranges = [part]
        part.location = start
        while ranges:
            part = ranges.pop()
            for p in self.rules[part.location].multi_process(part):
                if p.location in end:
                    yield p
                else:
                    ranges.append(p)

def main():
    input_data = '\n'.join(line.rstrip() for line in stdin.read().splitlines())
    document = Document(input_data)
    full_range = ((1,4001),)
    full_ranges = full_range * 4
    print(sum(part.combinations() for part in document.multi_classify(PartRange(full_ranges)) if part.location == 'A'))

if __name__ == '__main__':
    main()
