# -*- coding: utf-8 -*-

import re
from collections import MutableMapping
from termcolor import colored


class Intervals(MutableMapping):

    """Dictionary with intervals as keys and arbitrary data as values.

    An interval is a tuple of two integers, start and end.  Similar to a
    slice, start marks the first value of the interval while end is one
    past the last value of the interval.

    Public methods
    --------------

    overlap -- return all intervals overlapping the given interval

    """

    def __init__(self, intervals=None):
        self.data = {}
        if intervals is not None:
            for interval, value in intervals.iteritems():
                self[interval] = value

    def __setitem__(self, key, value):
        assert key[0] < key[1], \
          "End of interval must be strictly greater than its start"
        self.data[key] = value

    def __getitem__(self, key):
        return self.data[key]

    def __delitem__(self, key):
        del self.data[key]

    def __iter__(self):
        return iter(sorted(self.data))

    def __len__(self):
        return len(self.data)

    @classmethod
    def _interval_overlap(cls, interval1, interval2):
        """Return true if the two intervals overlap."""
        start1, end1 = interval1
        start2, end2 = interval2
        return start1 < end2 and end1 > start2

    def overlap(self, interval):
        """Return all intervals overlapping the given interval."""
        return set(i for i in self.data if self._interval_overlap(i, interval))


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
