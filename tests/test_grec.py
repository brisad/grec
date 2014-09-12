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
