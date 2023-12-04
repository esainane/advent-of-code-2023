#!/usr/bin/env python3

from sys import stdin
import re


def overlapping_findall(needle, haystack):
    """
    Find all matches of a regex in a string, including overlapping matches.

    The first capture group of the regex is presumed to be a capture of the
    result we want, while consuming no input. This can be accomplished by
    wrapping an existing regex in a lookahead with an inner capture:
    
        (?=(REGEX))

    re.finditer only finds non-overlapping matches, so we use a lookahead
    to make the match not consume any input, allowing us to find overlapping
    matches. The match is then found in the capture of the lookahead group.
    """
    return [m.group(1) for m in re.finditer(needle, haystack)]


# Note: By the puzzle spec, 'zero' isn't a valid digit
mapping = {
    'one': '1',
    'two': '2',
    'three': '3',
    'four': '4',
    'five': '5',
    'six': '6',
    'seven': '7',
    'eight': '8',
    'nine': '9'
}

# Build a regex that matches any of the words or digits
digit_finder = re.compile(f'(?=({"|".join(mapping.keys())}|[0-9]))')

def to_digit(match) -> str:
    """
    Convert a match to a digit, using the mapping if present in the mapping.
    """
    return mapping[match] if match in mapping else match

# Sum the calibration value across all input lines
total = 0
for line in stdin:
    # The value of a line is the concatenation of its first and last digit
    # Note that there may only be one digit, and we should still make a two
    # digit number out of it!
    digits = [to_digit(m) for m in overlapping_findall(digit_finder, line)]
    line_value = int(digits[0] + digits[-1])
    total += line_value

print(total)
