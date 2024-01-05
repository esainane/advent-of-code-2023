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

tick = 0

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

    def color(self) -> str:
        return 'black'

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

    def color(self):
        return 'red' if self.on else 'black'

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
        if self.source == 'lb' and high:
            d('lb received high pulse on tick', tick)
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

    def color(self):
        return 'red' if all(self.incoming.values()) else 'black'

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

class Done(Exception):
    pass

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
        button_presses = 0
        while True:
            try:
                button_presses += 1
                #d(state)
                state, low_pulses, high_pulses = self._pulse(state)
                total_low_pulses += low_pulses
                total_high_pulses += high_pulses
            except Done:
                return button_presses

    # State -> Destination State, Low pulses sent, High pulses sent
    #@functools.cache
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
                if t == 'rx' and not h:
                    raise Done()
                pulse_queue.append((target, t, h))

        #state = self.state()

        #d(state)

        return state, low_pulses, high_pulses


def do_dot(document: Document, filename: str):
    import pydot
    graph = pydot.Dot()

    terminal_nodes = []

    def label(name: str):
        if name in terminal_nodes:
            return name
        return document.rules[name].prefix + name

    for rule in document.rules.values():
        for target in rule.targets:
            if target in document.rules:
                continue
            terminal_nodes.append(target)
            graph.add_node(pydot.Node(label(target), label=label(target)))

    for rule in document.rules.values():
        graph.add_node(pydot.Node(label(rule.source), label=label(rule.source), color=rule.color()))
    for rule in document.rules.values():
        for target in rule.targets:
            graph.add_edge(pydot.Edge(label(rule.source), label(target), label=label(rule.source) + '->' + label(target)))

    graph.write_png(filename)

    # Solution by input analysis
    # There are four chains of flipflops each arranged around a central
    # conjunction, which is then inverted once more and sent into a
    # final conjunction with the output.
    # Each "bit" in a flipflop chain is either linked to or linked from
    # that chain's central flipflop.
    # In this input, there are four chains of 12 flipflops each, with
    # the following connection patterns. O is outbound toward the central
    # conjunction, I is inbound from the central conjunction, B is both, most
    # significant bit first:
    # - OOOOOOIOOIII (around th) active at 4095- 39=4056, resets to 0 at 4057
    # - OOOOIOIIIOOI (around pn) active at 4095-185=3910, resets to 0 at 3911
    # - OOOOOOOIOOOI (around fz) active at 4095- 17=4078, resets to 0 at 4079
    # - OOOOIIOIIOIB (around vd) active at 4095-219=3876, resets to 0 at 3877

def gcd(a: int, b: int) -> int:
    while b:
        a, b = b, a % b
    return a

def lcm(a: int, b: int) -> int:
    return a * b // gcd(a, b)

def main():
    input_data = '\n'.join(line.rstrip() for line in stdin.read().splitlines())
    document = Document(input_data)

    do_dot(document, '20p2/20p2s0.png')
    show_state = set((3876, 3877, 3910, 3911, 4056, 4057, 4078, 4079, 4080, 4081, 3877 * 2))
    for i in range(1, 8000):
        global tick
        tick = i
        document._pulse(None)
        if i in show_state:
            do_dot(document, f'20p2/20p2s{i}.png')
    do_dot(document, f'20p2/20p2s{i}.png')

    print(lcm(lcm(4057,3911),lcm(4079,3877)))
    # For fun: See if they have no factors in common
    print(functools.reduce(lambda a, b: a * b, (4057,3911,4079,3877)))


if __name__ == '__main__':
    main()
