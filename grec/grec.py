# -*- coding: utf-8 -*-

import re
from termcolor import colored


class ColoredString(object):
    """Apply color to different parts of a string."""

    def __init__(self, string):
        self.string = string
        self.parts = []

    def apply_color(self, start, end, color_info):
        self.parts.append((start, end, color_info))

    def __str__(self):
        ret = ""
        offset = 0
        for start, end, color_info in self.parts:
            ret += self.string[offset:start] + \
              colored(self.string[start:end], *color_info)
            offset = end
        ret += self.string[offset:]
        return ret


class Matcher(object):
    """Colorize text based on regular expression matches."""

    def __init__(self):
        self.patterns = []

    def add_pattern(self, pattern, foreground=None, background=None):
        self.patterns.append((pattern, foreground, background))

    def match(self, text):
        colored_string = ColoredString(text)

        for rule in self.patterns:
            pattern = re.compile(rule[0])
            color_info = rule[1:]

            for re_match in pattern.finditer(text):
                start, end = re_match.span()
                colored_string.apply_color(start, end, color_info)

        return colored_string
