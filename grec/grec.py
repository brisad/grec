# -*- coding: utf-8 -*-

import re
from termcolor import colored


class Matcher(object):
    """Colorize text based on regular expression matches."""

    def __init__(self):
        self.patterns = []

    def add_pattern(self, pattern, foreground=None, background=None):
        self.patterns.append((pattern, foreground, background))

    def _color_text(self, text, descriptors):
        ret = ""
        offset = 0
        for start, end, color_info in descriptors:
            ret += text[offset:start] + colored(text[start:end], *color_info)
            offset = end
        ret += text[offset:]
        return ret

    def match(self, text):
        for rule in self.patterns:
            pattern = re.compile(rule[0])
            color_info = rule[1:]

            color_descriptors = []

            for re_match in pattern.finditer(text):
                start, end = re_match.span()
                color_descriptors.append((start, end, color_info))

            text = self._color_text(text, color_descriptors)

        return text
