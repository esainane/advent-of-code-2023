#!/usr/bin/env python3

from collections import defaultdict
from sys import stdin
from typing import List

# Make use of pyparsing to cleanly handle all the input boilerplate

from pyparsing import Word, alphas, delimitedList, Keyword, Optional, Group, ZeroOrMore, ParseResults

# The grammar is as follows:

# game_line     ::= "Game " game_number ": " cube_set_list
# game_number   ::= [0-9]+
# cube_set_list ::= cube_set (";" cube_set)*
# cube_set      ::= cube ("," cube)*
# cubes         ::= cube_count cube_color
# cube_count    ::= [0-9]+
# cube_color    ::= [a-z]+

# Build the parser

game_number = Word('0123456789')
cube_count = Word('0123456789')
cube_color = Word(alphas)
cubes = Group(cube_count + cube_color)
cube_set = Group(delimitedList(cubes))
cube_set_list = delimitedList(cube_set, delim=';')
game_line = Keyword("Game") + game_number + ':' + cube_set_list

class CubeSet(object):
    def __init__(self, cube_set: ParseResults):
        # Cube set is pre-parsed from Game
        # Get the sum of all cubes of each color
        self.cube_count = defaultdict(int)
        for cubes in cube_set:
            self.cube_count[cubes[1]] += int(cubes[0])
        #print("Cube set: ", self.cube_count)

    def check_possible(self):
        '''
        A cube set is considered "possible" if it uses no more than:
         - 12 red
         - 13 green
         - 14 blue
        and impossible otherwise.
        '''
        return self.cube_count['red'] <= 12 and self.cube_count['green'] <= 13 and self.cube_count['blue'] <= 14

class Game(object):
    def __init__(self, input_game_line: str):
        # Parse our game line
        result = game_line.parse_string(input_game_line, parse_all=True)
        self.game_line = result
        self.game_number = int(self.game_line[1])
        self.cube_sets = [CubeSet(s) for s in self.game_line[3:]]

    def check_possible(self):
        '''
        A game is considered "possible" if all cube sets in it are possible.
        '''
        return all(cube_set.check_possible() for cube_set in self.cube_sets)


# Parse all games
games = [Game(line.rstrip()) for line in stdin]

# Print the sum of the IDs of all possible games
print(sum(game.game_number for game in games if game.check_possible()))
