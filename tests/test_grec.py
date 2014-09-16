#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_grec
----------------------------------

Tests for `grec` module.
"""

import pytest
import grec

def test_literal():
    m = grec.Matcher()
    m.add_pattern('x', 'blue')
    assert str(m.match('axbxc')) == 'a\x1b[34mx\x1b[0mb\x1b[34mx\x1b[0mc'

def test_literal_with_background():
    m = grec.Matcher()
    m.add_pattern('x', 'blue', 'on_white')
    assert str(m.match('axbxc')) == 'a\x1b[47m\x1b[34mx\x1b[0mb\x1b[47m\x1b[34mx\x1b[0mc'

def test_wildcard():
    m = grec.Matcher()
    m.add_pattern('x.x', 'red')
    assert str(m.match('axbxc')) == 'a\x1b[31mxbx\x1b[0mc'

def test_add_pattern_same_replaces():
    m = grec.Matcher()
    m.add_pattern('axbxc', 'red')
    m.add_pattern('b', 'blue')
    m.add_pattern('axbxc', 'green')
    assert str(m.match('axbxc')) == '\x1b[32maxbxc\x1b[0m'
    assert len(m.patterns) == 2

def test_remove_pattern():
    m = grec.Matcher()
    m.add_pattern('x', 'red')
    m.remove_pattern('x')
    assert str(m.match('axbxc')) == 'axbxc'

def test_multiple_patterns():
    m = grec.Matcher()
    m.add_pattern('a', 'red')
    m.add_pattern('b', 'green')
    m.add_pattern('c', 'blue')
    assert str(m.match('axbxc')) == '\x1b[31ma\x1b[0mx\x1b[32mb\x1b[0mx\x1b[34mc\x1b[0m'

def test_overlapping_patterns():
    m = grec.Matcher()
    m.add_pattern('ax', 'red')
    m.add_pattern('xc', 'green')
    m.add_pattern('xbx', 'blue')
    assert str(m.match('axbxc')) == '\x1b[31ma\x1b[0m\x1b[34mxbx\x1b[0m\x1b[32mc\x1b[0m'
    m = grec.Matcher()
    m.add_pattern('axbxc', 'blue')
    m.add_pattern('xbx', 'red')
    assert str(m.match('axbxc')) == '\x1b[34ma\x1b[0m\x1b[31mxbx\x1b[0m\x1b[34mc\x1b[0m'
    m = grec.Matcher()
    m.add_pattern('axb', 'green')
    m.add_pattern('xb', 'blue')
    assert str(m.match('axbxc')) == '\x1b[32ma\x1b[0m\x1b[34mxb\x1b[0mxc'
    m = grec.Matcher()
    m.add_pattern('axb', 'green')
    m.add_pattern('ax', 'blue')
    assert str(m.match('axbxc')) == '\x1b[34max\x1b[0m\x1b[32mb\x1b[0mxc'

def test_intervals_overlap():
    intervals = grec.grec.Intervals({(1, 5): None, (6, 8): None})
    assert intervals.overlap((0, 1)) == set()
    assert intervals.overlap((1, 2)) == set([(1, 5)])
    assert intervals.overlap((1, 6)) == set([(1, 5)])
    assert intervals.overlap((5, 6)) == set()
    assert intervals.overlap((4, 10)) == set([(1, 5), (6, 8)])
    assert intervals.overlap((5, 10)) == set([(6, 8)])
    assert intervals.overlap((10, 10)) == set()

def test_intervals_mutable_mapping():
    intervals = grec.grec.Intervals()
    intervals[(5, 10)] = 'abc'
    assert intervals[(5, 10)] == 'abc'
    assert intervals == {(5, 10): 'abc'}
    intervals[(1, 2)] = 'def'
    assert intervals.keys() == [(1, 2), (5, 10)]  # Sorted order
    assert len(intervals) == 2
    del intervals[(1, 2)]
    assert len(intervals) == 1

def test_bad_interval():
    intervals = grec.grec.Intervals()
    with pytest.raises(AssertionError):
        intervals[(0, 0)] = 'ghi'
    with pytest.raises(AssertionError):
        intervals = grec.grec.Intervals({(1, 1): None})
