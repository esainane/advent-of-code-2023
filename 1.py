#!/usr/bin/env python3

from sys import stdin

# Sum the calibration value across all input lines
total = 0
for line in stdin:
    # The value of a line is the concatenation of its first and last digit
    # Note that there may only be one digit, and we should still make a two
    # digit number out of it!
    digits_in_line = ''.join(c for c in line if c.isdigit())
    line_value = int(digits_in_line[0] + digits_in_line[-1])
    total += line_value

print(total)
