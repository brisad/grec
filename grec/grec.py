# -*- coding: utf-8 -*-

"""Colorize terminal text with regular expressions.

This module implements all functionality required for grec.

"""

import sys
import argparse
import re

try:
    # Python 2
    from itertools import izip_longest as zip_longest
except ImportError:
    # Python 3
    from itertools import zip_longest

from collections import MutableMapping, OrderedDict
from termcolor import colored, COLORS, HIGHLIGHTS


class Intervals(MutableMapping):

    """Dictionary with intervals as keys and arbitrary data as values.

    Used to check whether intervals overlap.

    An interval is a tuple of two integers, *start* and *end*.  Like a
    slice, *start* marks the first value of the interval while *end* is
    one past the last value of the interval.

    """

    def __init__(self, intervals=None):
        self.data = {}
        if intervals is not None:
            for interval, value in intervals.items():
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
        """Return all intervals in dict overlapping the given interval.

        :param tuple interval: start and end of interval

        """

        return set(i for i in self.data if self._interval_overlap(i, interval))


class ColoredString(object):

    """String with colorized parts.

    :ivar string: The plain string without any color information.
    :ivar intervals: :class:`Intervals` instance associating intervals
                     with colors.

    """

    def __init__(self, string):
        self.string = string
        self.intervals = Intervals()

    def apply_color(self, start, end, color_info):
        """Apply color to all characters within an interval.

        :param int start: index of first character in string to colorize
        :param int end: index of one past the last character to colorize
        :param tuple color_info: foreground and background color as strings

        The characters of the string that have indices *start* through
        *end* - 1 will be assigned the colors specified in *color_info*.

        If any characters in the interval already have a color set,
        their color will be replaced with the new color.

        The strings in *color_info* need to be recognized by
        :mod:`termcolor`.

        >>> s = ColoredString('a word with color')
        >>> s.apply_color(2, 6, ('red', 'on_white'))
        >>> print(s)
        a \x1b[47m\x1b[31mword\x1b[0m with color

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
        """Return string with ANSI escape codes for colors."""
        offset = 0
        segments = []
        for (start, end), color_info in self.intervals.items():
            segments.append(self.string[offset:start])
            segments.append(colored(self.string[start:end], *color_info))
            offset = end
        segments.append(self.string[offset:])
        return ''.join(segments)


class Matcher(object):

    """Colorize text based on regular expression matches.

    :ivar patterns: :class:`OrderedDict` of all configured patterns

    >>> m = Matcher()
    >>> m.add_pattern('A', 'red')
    >>> m.add_pattern('B.', 'blue')
    >>> colored = m.match('ABC')
    >>> colored.string
    'ABC'
    >>> print(colored)
    \x1b[31mA\x1b[0m\x1b[34mBC\x1b[0m

    """

    def __init__(self):
        """Create new instance, containing no patterns."""
        self.patterns = OrderedDict()

    @staticmethod
    def _termcolor_names(foreground, background=None):
        """Translate color names to ones recognized by termcolor.

        termcolor.colored expects backgrounds to be specified as
        'on_white', 'on_red', and so on.

        Raises ValueError if foreground or background is not recognized
        by termcolor.

        """

        # Save the name in case we need to raise an error
        original_bg = background
        if background is not None:
            background = 'on_' + background

        if foreground and foreground not in COLORS:
            raise ValueError("Color '{}' not recognized".format(foreground))

        if background and background not in HIGHLIGHTS:
            raise ValueError("Color '{}' not recognized".format(original_bg))

        return (foreground, background)

    def _add_to_patterns(self, regex, pattern):
        """Add new pattern to patterns instance variable.

        If the associated regular expression is already present in
        self.patterns it will first be removed to ensure replacement.

        """

        if regex in self.patterns:
            del self.patterns[regex]
        self.patterns[regex] = pattern

    def add_pattern(self, regex, foreground=None, background=None):
        """Add regular expression for text colorization.

        :param string regex: regular expression
        :param string foreground: foreground color
        :param string background: background color

        The order of additions is significant.  Matching and
        colorization will be applied in the same order as they are added
        with this method.

        If the passed regular expression *regex* is identical to an
        already added one (color information not considered), then that
        old pattern will be replaced with this one.  The ordering will
        still be updated, so any other already present patterns will be
        processed before this one when matching.

        >>> m = Matcher()
        >>> m.add_pattern('^$', 'red')
        >>> m.add_pattern('[A-Z]+', 'blue', 'white')

        """

        self._add_to_patterns(regex, {
            'group': False,
            'regex': re.compile(regex),
            'color_info': self._termcolor_names(foreground, background)
            })

    def add_group_pattern(self, regex, *args):
        """Add regular expression with groups for text colorization.

        :param string regex: regular expression
        :param tuple args: color information for each matched group

        Works like :func:`add_pattern` but colors matched groups instead
        of the whole match.

        Takes a variable number of arguments where each is a tuple with
        color information: *(foreground, background)*.  These will be
        used to colorize the corresponding group matches in the same
        order.

        When a regular expression contains more groups than colors, the
        color information specified in the last argument is repeated for
        all remaining groups.

        When a regular expression contains less groups than colors then
        excess colors are ignored.

        >>> m = Matcher()
        >>> m.add_group_pattern('^#.*(ERROR)', ('red',))
        >>> m.add_group_pattern('A(B)C(D)', ('blue', 'white'), ('red',))

        """

        self._add_to_patterns(regex, {
            'group': True,
            'regex': re.compile(regex),
            'color_info': [self._termcolor_names(*colors) for colors in args]
            })

    def remove_pattern(self, regex):
        """Remove the pattern with the given regular expression.

        :param string regex: regular expression of a previously added pattern

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
        """Colorize text according to pattern matches.

        :param string text: string to match for colorization
        :rtype: :class:`ColoredString` instance

        Returns a :class:`ColoredString` which may or may not have an
        actual color, depending on whether any patterns matched the
        passed string.

        Printing the instance in the terminal will show the string with
        its assigned colors.

        >>> m = Matcher()
        >>> m.add_pattern('5', 'red')
        >>> colored_string = m.match('1 2 3 4 5')
        >>> colored_string  # doctest: +ELLIPSIS
        <grec....ColoredString object at 0x...>
        >>> print(colored_string)
        1 2 3 4 \x1b[31m5\x1b[0m

        """

        colored_string = ColoredString(text)

        for pattern in self.patterns.values():
            for re_match in pattern['regex'].finditer(text):
                if pattern['group']:
                    # If this is a group pattern, we need to iterate
                    # over and colorize all groups.
                    intervals = re_match.regs[1:]
                    colors = pattern['color_info']
                else:
                    # Otherwise, we only have one interval to
                    # colorize: the span of the whole match.
                    intervals = (re_match.span(),)
                    colors = (pattern['color_info'],)

                # If there are more colors than intervals, truncate
                # the list of colors to have the same length as
                # intervals.
                colors = colors[:len(intervals)]
                # Skip the colorization if we ended up with no colors.
                if not colors:
                    continue

                # Pair up intervals with their colors.  If there are
                # more intervals than colors then fill up the missing
                # colors with the last color in the colors array.
                pairs = zip_longest(intervals, colors, fillvalue=colors[-1])
                for (start, end), color_info in pairs:
                    colored_string.apply_color(start, end, color_info)

        return colored_string

    def match_iter(self, iterable):
        """Return an iterator of match results.

        :param iterable: iterable of strings to match
        :rtype: iterator

        For each string in *iterable*, the returned iterator yields a
        :class:`ColoredString` instance which is the result of
        performing a pattern match on the string.

        >>> m = Matcher()
        >>> m.add_pattern('2', 'green')
        >>> for colored_string in m.match_iter(['1', '2', '3']):
        ...     print(colored_string)
        1
        \x1b[32m2\x1b[0m
        3

        """

        for line in iterable:
            yield self.match(line)


class PatternAction(argparse.Action):

    """Action class to handle pattern arguments with argparse.

    To retain ordering between *-m* and *-g* arguments from command-line
    input, this class aggregates them in order into a list.

    """

    def __call__(self, parser, namespace, values, option_string=None):
        if not 'pattern_data' in namespace:
            # For the first pattern, create the (empty) attribute
            setattr(namespace, 'pattern_data', [])

        # Append next pattern to 'pattern_data'
        previous = namespace.pattern_data
        previous.append((self.dest, values))
        setattr(namespace, 'pattern_data', previous)


def parse_arguments(args):
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description='Colorize text by regular expressions',
        usage='grec [-h] [-m PATTERN COLOR_INFO] '
        '[-g PATTERN [COLOR_INFO ...]] -- file')
    parser.add_argument('-m', dest='normal', nargs=2,
                        action=PatternAction,
                        metavar=('PATTERN', 'COLOR_INFO'),
                        help='colorize each occurence of PATTERN '
                        'with the colors specified in COLOR_INFO. '
                        'This argument can be used multiple times.')
    parser.add_argument('-g', dest='group', nargs='+',
                        action=PatternAction,
                        metavar=('PATTERN', 'COLOR_INFO'),
                        help='colorize all groups in each '
                        'occurence of PATTERN with the colors  '
                        'specified in COLOR_INFO. The number of '
                        ' colors should match the number of groups '
                        'in the regular expression. '
                        'This argument can be used multiple times.')
    parser.add_argument('file', type=argparse.FileType('r'),
                        nargs='?', default=sys.stdin,
                        help="file whose contents to colorize ('-' for stdin)")
    return parser.parse_args(args)

def split_colors(color):
    """Convert color from command line into foreground and background.

    :param string color: color(s) to translate

    Backgrounds can be optionally prepended by 'on'.

    >>> split_colors("yellow")
    ['yellow']
    >>> split_colors("red_on_blue")
    ['red', 'blue']
    >>> split_colors("green white")
    ['green', 'white']

    """

    return [item for item in re.split(r'\W+|_', color) if item != 'on']

def main(args=None):
    """Run grec command."""
    args = parse_arguments(args)

    matcher = Matcher()
    for pattern_type, pattern in args.pattern_data:
        # Regex and color(s) from command line
        regex, colors = pattern[0], pattern[1:]

        # Patterns can be of normal or of group type
        if pattern_type == 'normal':
            # Here we only have one color for the whole match.
            assert len(colors) == 1
            color_info = split_colors(colors[0])
            matcher.add_pattern(regex, *color_info)
        elif pattern_type == 'group':
            # For group patterns we use multiple colors
            color_info = [split_colors(color) for color in colors]
            matcher.add_group_pattern(regex, *color_info)

    for colored_string in matcher.match_iter(args.file):
        sys.stdout.write(str(colored_string))

    return 0
