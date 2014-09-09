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
    m.add_pattern('x')
    assert str(m.match('axbxc')) == 'a\x1b[31mx\x1b[0mb\x1b[31mx\x1b[0mc'
