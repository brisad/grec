#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_grec
----------------------------------

Tests for `grec` module.
"""

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

def test_multiple_patterns():
    m = grec.Matcher()
    m.add_pattern('a', 'red')
    m.add_pattern('b', 'green')
    m.add_pattern('c', 'blue')
    assert str(m.match('axbxc')) == '\x1b[31ma\x1b[0mx\x1b[32mb\x1b[0mx\x1b[34mc\x1b[0m'
