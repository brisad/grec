# -*- coding: utf-8 -*-

import re
from termcolor import colored


class Matcher(object):
    """Colorize text based on regular expression matches."""

    def __init__(self):
        self.patterns = []

    def add_pattern(self, pattern, foreground=None, background=None):
        self.patterns.append((pattern, foreground, background))

    def match(self, text):
        ret = ""
        pattern = self.patterns[0]

        re_match = re.search(pattern[0], text)
        while re_match:
            start, end = re_match.span()
            ret += text[:start] + colored(text[start:end], *pattern[1:])
            text = text[end:]
            re_match = re.search(pattern[0], text)
        ret += text
        return ret
