#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_grec
----------------------------------

Tests for `grec` module.
"""

import pytest
import grec


class TestMatcher(object):

    @pytest.fixture
    def matcher(self):
        return grec.Matcher()

    def check(self, matcher, result_string):
        assert str(matcher.match('axbxc')) == result_string

    def test_literal(self, matcher):
        matcher.add_pattern('x', 'blue')
        self.check(matcher, 'a\x1b[34mx\x1b[0mb\x1b[34mx\x1b[0mc')

    def test_literal_with_background(self, matcher):
        matcher.add_pattern('x', 'blue', 'white')
        self.check(matcher,
                   'a\x1b[47m\x1b[34mx\x1b[0mb\x1b[47m\x1b[34mx\x1b[0mc')

    def test_wildcard(self, matcher):
        matcher.add_pattern('x.x', 'red')
        self.check(matcher, 'a\x1b[31mxbx\x1b[0mc')

    def test_add_pattern_same_replaces(self, matcher):
        matcher.add_pattern('axbxc', 'red')
        matcher.add_pattern('b', 'blue')
        matcher.add_pattern('axbxc', 'green')
        self.check(matcher, '\x1b[32maxbxc\x1b[0m')
        assert len(matcher.patterns) == 2

    def test_remove_pattern(self, matcher):
        matcher.add_pattern('x', 'red')
        matcher.remove_pattern('x')
        self.check(matcher, 'axbxc')

    def test_multiple_patterns(self, matcher):
        matcher.add_pattern('a', 'red')
        matcher.add_pattern('b', 'green')
        matcher.add_pattern('c', 'blue')
        self.check(matcher,
                   '\x1b[31ma\x1b[0mx\x1b[32mb\x1b[0mx\x1b[34mc\x1b[0m')

    def test_partial_overlap(self, matcher):
        matcher.add_pattern('ax', 'red')
        matcher.add_pattern('xc', 'green')
        matcher.add_pattern('xbx', 'blue')
        self.check(matcher,
                   '\x1b[31ma\x1b[0m\x1b[34mxbx\x1b[0m\x1b[32mc\x1b[0m')

    def test_overlap_new_interval_within(self, matcher):
        matcher.add_pattern('axbxc', 'blue')
        matcher.add_pattern('xbx', 'red')
        self.check(matcher,
                   '\x1b[34ma\x1b[0m\x1b[31mxbx\x1b[0m\x1b[34mc\x1b[0m')

    def test_overlap_right_aligned(self, matcher):
        matcher.add_pattern('axb', 'green')
        matcher.add_pattern('xb', 'blue')
        self.check(matcher, '\x1b[32ma\x1b[0m\x1b[34mxb\x1b[0mxc')

    def test_overlap_left_aligned(self, matcher):
        matcher.add_pattern('axb', 'green')
        matcher.add_pattern('ax', 'blue')
        self.check(matcher, '\x1b[34max\x1b[0m\x1b[32mb\x1b[0mxc')


class TestIntervals(object):

    def test_intervals_overlap(self):
        intervals = grec.grec.Intervals({(1, 5): None, (6, 8): None})
        assert intervals.overlap((0, 1)) == set()
        assert intervals.overlap((1, 2)) == set([(1, 5)])
        assert intervals.overlap((1, 6)) == set([(1, 5)])
        assert intervals.overlap((5, 6)) == set()
        assert intervals.overlap((4, 10)) == set([(1, 5), (6, 8)])
        assert intervals.overlap((5, 10)) == set([(6, 8)])
        assert intervals.overlap((10, 10)) == set()

    def test_intervals_mutable_mapping(self):
        intervals = grec.grec.Intervals()
        intervals[(5, 10)] = 'abc'
        assert intervals[(5, 10)] == 'abc'
        assert intervals == {(5, 10): 'abc'}
        intervals[(1, 2)] = 'def'
        assert intervals.keys() == [(1, 2), (5, 10)]  # Sorted order
        assert len(intervals) == 2
        del intervals[(1, 2)]
        assert len(intervals) == 1

    def test_bad_interval(self):
        intervals = grec.grec.Intervals()
        with pytest.raises(AssertionError):
            intervals[(0, 0)] = 'abc'
        with pytest.raises(AssertionError):
            intervals = grec.grec.Intervals({(1, 1): None})
