# -*- coding: utf-8 -*-

import re
from collections import MutableMapping, OrderedDict
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

    """Apply color to different parts of a string.

    Instance variables
    ------------------

    string -- the string without any color
    intervals -- Intervals instance associating intervals with colors

    """

    def __init__(self, string):
        self.string = string
        self.intervals = Intervals()

    def apply_color(self, start, end, color_info):
        """Apply color to all characters within given interval.

        The characters of the string that have indices start through
        end - 1 will be assigned the colors specified in color_info.

        If any characters in the interval already have a color set,
        their color will be replaced with the new color.

        Parameters
        ----------

        start -- index of first character in string to colorize
        end -- index of one past the last character to colorize
        color_info -- tuple of foreground and background color

        """

        # Find any overlapping colorized intervals.  If found we need
        # to truncate them to make room for the new interval.
        for interval in self.intervals.overlap((start, end)):
            other_start, other_end = interval
            # Save the parts that aren't obscured by the new interval.
            # Those can only be on the left and right side of the new
            # interval.
            if other_start < start:
                self.intervals[(other_start, start)] = self.intervals[interval]
            if end < other_end:
                self.intervals[(end, other_end)] = self.intervals[interval]
            # Delete original interval
            del self.intervals[interval]

        # When there's no more overlapping intervals, set our new one
        # with its associated color
        self.intervals[(start, end)] = color_info

    def __str__(self):
        offset = 0
        segments = []
        for (start, end), color_info in self.intervals.iteritems():
            segments.append(self.string[offset:start])
            segments.append(colored(self.string[start:end], *color_info))
            offset = end
        segments.append(self.string[offset:])
        return ''.join(segments)


class Matcher(object):

    """Colorize text based on regular expression matches.

    Instance variables
    ------------------

    patterns -- OrderedDict of all configured patterns

    Example
    -------

    >>> m = Matcher()
    >>> m.add_pattern('A', 'red')
    >>> m.add_pattern('B.', 'blue')
    >>> colored = m.match('ABC')
    >>> colored.string
    'ABC'
    >>> print colored
    \x1b[31mA\x1b[0m\x1b[34mBC\x1b[0m

    """

    def __init__(self):
        self.patterns = OrderedDict()

    def add_pattern(self, regex, foreground=None, background=None):
        """Add regular expression for text colorization.

        The order of additions is significant.  Matching and
        colorization will be applied in the same order as they are added
        with this method.

        If the passed regular expression is identical to an already
        added one (color information not considered), then that old
        pattern will be replaced with this one.  The ordering will still
        be updated, so any other already present patterns will be
        processed before this one when matching.

        Parameters
        ----------

        regex -- regular expression
        foreground -- foreground color
        background -- background color

        Example
        -------

        >>> m = Matcher()
        >>> m.add_pattern('^$', 'red')
        >>> m.add_pattern('[A-Z]+', 'blue', 'on_white')

        """

        if regex in self.patterns:
            del self.patterns[regex]
        self.patterns[regex] = (re.compile(regex), (foreground, background))

    def remove_pattern(self, regex):
        """Remove the pattern with given regular expression.

        Parameters
        ----------

        regex -- regular expression of a previously added pattern

        Example
        -------

        >>> m = Matcher()
        >>> m.add_pattern('[A-Z]', 'blue')
        >>> len(m.patterns)
        1
        >>> m.remove_pattern('[A-Z]')
        >>> len(m.patterns)
        0

        """

        del self.patterns[regex]

    def match(self, text):
        """Colorize string according to pattern matches."""
        colored_string = ColoredString(text)

        for pattern, color_info in self.patterns.itervalues():
            for re_match in pattern.finditer(text):
                start, end = re_match.span()
                colored_string.apply_color(start, end, color_info)

        return colored_string
