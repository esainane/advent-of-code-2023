#!/usr/bin/env python3

import functools
from sys import stderr, stdin
from typing import Any, Dict, List, Set

from pyparsing import alphanums, delimitedList, nums, Group, Iterable, Literal, OneOrMore, Optional, ParseResults, Tuple, Word


def d(*args, **kwargs):
    print(file=stderr, *args, **kwargs)
    pass


number = Word(nums)
name = Word(alphanums)

prefix = Optional(Literal('&') | Literal('%'))('prefix')
rule = prefix + name('source') + Literal('->') + delimitedList(name)('targets')

document = OneOrMore(Group(rule))('rules')

class Rule(object):
    def __init__(self, source: str, targets: Iterable[str], prefix: str):
        self.source = source
        self.targets = targets
        self.prefix = prefix

    def notify_incoming(self, rule: 'Rule') -> None:
        pass

    def pulse(self, source: str, high: bool) -> Iterable[Tuple[str, bool]]:
        raise NotImplementedError()

    def state(self) -> Any:
        return None

    def load_state(self, state: Any) -> None:
        pass

class FlipFlop(Rule):
    def __init__(self, source: str, targets: Iterable[str]):
        super().__init__(source, targets, '%')
        self.on: bool = False

    def pulse(self, source: str, high: bool) -> Iterable[Tuple[str, bool]]:
        #d('flipflop pulse')
        if not high:
            self.on = not self.on
            for target in self.targets:
                yield target, self.on

    def state(self) -> Any:
        return self.on

    def load_state(self, state: Any) -> None:
        self.on = state

class Conjunction(Rule):
    def __init__(self, source: str, targets: Iterable[str]):
        super().__init__(source, targets, '&')
        self.incoming = {}

    def notify_incoming(self, rule: 'Rule') -> None:
        self.incoming[rule.source] = False

    def pulse(self, source: str, high: bool) -> Iterable[Tuple[str, bool]]:
        #d('conjunction pulse')
        assert(source in self.incoming)
        self.incoming[source] = high
        if all(self.incoming.values()):
            for target in self.targets:
                yield target, False
        else:
            for target in self.targets:
                yield target, True

    def state(self) -> Any:
        return tuple(v for k, v in sorted(self.incoming.items()))

    def load_state(self, state: Any) -> None:
        for k, v in zip(sorted(self.incoming.keys()), state):
            self.incoming[k] = v

class Broadcaster(Rule):
    def __init__(self, targets: Iterable[str]):
        super().__init__('broadcaster', targets, '')

    def pulse(self, source: str, high: bool) -> Iterable[Tuple[str, bool]]:
        #d('broadcaster pulse')
        for target in self.targets:
            yield target, high

def make_rule(source: str, targets: Iterable[str], prefix: str) -> Rule:
    if prefix == '%':
        return FlipFlop(source, targets)
    elif prefix == '&':
        return Conjunction(source, targets)
    else:
        assert(source == 'broadcaster')
        return Broadcaster(targets)

SystemState = Tuple[Any]

class Document(object):
    def __init__(self, input_data: str):
        result = self.result = document.parse_string(input_data, parseAll=True)
        rules = self.rules = {}

        for rule in result.rules:
            #d(rule)
            assert(rule.source not in rules)
            rule = make_rule(rule.source, rule.targets, rule.prefix)
            rules[rule.source] = rule

        assert('broadcaster' in rules)

        for rule in rules.values():
            for target in rule.targets:
                #d(target)
                if target not in rules:
                    continue
                rules[target].notify_incoming(rule)

        self.state_order = sorted(rules.keys())
        d(self.state_order)

    def state(self) -> Any:
        return tuple(self.rules[rule].state() for rule in self.state_order)

    def load_state(self, state: Any) -> None:
        for rule, s in zip(self.state_order, state):
            self.rules[rule].load_state(s)

    def pulses(self, count: int) -> int:
        total_low_pulses = total_high_pulses = 0
        state = self.state()
        #d(state)
        for _ in range(count):
            #d(state)
            state, low_pulses, high_pulses = self._pulse(state)
            total_low_pulses += low_pulses
            total_high_pulses += high_pulses
        d(total_low_pulses, total_high_pulses)
        return total_low_pulses * total_high_pulses

    # State -> Destination State, Low pulses sent, High pulses sent
    @functools.cache
    def _pulse(self, state: SystemState) -> Tuple[SystemState, int, int]:
        #d('running pulse')
        #self.load_state(state)

        pulse_queue: List[Tuple[str, str, bool]] = []
        pulse_queue.append(('button', 'broadcaster', False))
        high_pulses = low_pulses = 0
        while pulse_queue:
            source, target, high = pulse_queue.pop(0)
            if high:
                high_pulses += 1
            else:
                low_pulses += 1
            #d(source, f'-{"high" if high else "low"}->', target)
            if target not in self.rules:
                continue
            assert(self.rules[target])
            for t, h in self.rules[target].pulse(source, high):
                pulse_queue.append((target, t, h))

        state = self.state()

        #d(state)

        return state, low_pulses, high_pulses




def main():
    input_data = '\n'.join(line.rstrip() for line in stdin.read().splitlines())
    document = Document(input_data)

    print(document.pulses(1000))


if __name__ == '__main__':
    main()
