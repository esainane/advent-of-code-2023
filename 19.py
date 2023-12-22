#!/usr/bin/env python3

from sys import stdin
from typing import Set

from pyparsing import alphanums, nums, Group, Literal, OneOrMore, ParseResults, Word


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

def comparator_str_to_func(comparator: str):
    if comparator == '=':
        return lambda p, v: p == v
    if comparator == '<':
        return lambda p, v: p < v
    if comparator == '>':
        return lambda p, v: p > v

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
        self.comparator = comparator_str_to_func(conditional.comparator)
        self.value = int(conditional.value)
        self.destination = conditional.destination
    
    def test(self, part) -> bool:
        return self.comparator(part.properties[self.property], self.value)

    def __repr__(self):
        return f'<Conditional {self.property}, {self.comparator}, {self.value}, {self.destination}>'

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

def main():
    input_data = '\n'.join(line.rstrip() for line in stdin.read().splitlines())
    document = Document(input_data)
    print(sum(part.rated_value() for part in document.parts if document.classify(part) == 'A'))

if __name__ == '__main__':
    main()
