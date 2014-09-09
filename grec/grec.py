# -*- coding: utf-8 -*-

import re
from termcolor import colored


class Matcher(object):
    """Colorize text based on regular expression matches."""

    def __init__(self):
        self.patterns = []

    def add_pattern(self, pattern):
        self.patterns.append(pattern)

    def match(self, text):
        return re.sub(self.patterns[0], colored(self.patterns[0], 'red'), text)
