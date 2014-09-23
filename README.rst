===============================
grec
===============================

.. image:: https://badge.fury.io/py/grec.png
    :target: http://badge.fury.io/py/grec

.. image:: https://travis-ci.org/brisad/grec.png?branch=master
        :target: https://travis-ci.org/brisad/grec

.. image:: https://pypip.in/d/grec/badge.png
        :target: https://pypi.python.org/pypi/grec


Colorize terminal text with regular expressions.

* Free software: BSD license
* Documentation: https://grec.readthedocs.org.

Features
--------

`grec` is similar to `grep`; the difference being that instead of
printing matching lines in a file, `grec` colorizes lines.  Lines that
do not match any pattern are still printed, but without color.

The key feature that separates this utility from other similar ones is
that it's possible to colorize a matching string several times without
letting previously matched colors mess up following regular expression
matches.


Quick Start
-----------

Install with `pip`::

    pip install grec

Print the contents of `log_file.txt` in its entirety but also colorize
any occurrences of errors and warnings::

    grec -m ERROR red -m WARN yellow log_file.txt

Or use a pipe::

    cat log_file.txt | grec -m ERROR red -m WARN yellow -

Command line
------------

The command line interface is the following::

    grec -m PATTERN COLOR_INFO [-m ... ] file

The `-m` argument
~~~~~~~~~~~~~~~~~

This argument takes a regular expression and color information.
Here's an example that will make all lines starting with the character
"#" have a green color with white background::

    -m '^#.*' green_on_white

Whenever a line matches the regular expression, the part of the line
that matched is colorized with the color information.  Any number of
`-m` arguments can be specified, and colorization will be applied in
the order specified on the command line.

The regular expression will be matched by the `re` module.  So for
each regular expression, only non-overlapping matches will be
colorized.  To get overlapping matches use several patterns by adding
more `-m` arguments.

Color information consists of a foreground and optionally a
background.  Colorization is performed with the `termcolor` package
and thus the following colors are supported: *grey*, *red*, *green*,
*yellow*, *blue*, *magenta*, *cyan*, *white*.

To only set the foreground color, simply specify the name of the
color.  To also set a background color, add it to the foreground
color.  Use quotes or underlines to prevent the shell from
interpreting it as several arguments.  Examples::

    -m <regex> blue_on_yellow
    -m <regex> blue_yellow
    -m <regex> 'blue on yellow'
    -m <regex> 'blue yellow'

The file argument
~~~~~~~~~~~~~~~~~

This is the file to colorize.  If "-" is specified, `stdin` will be
read instead and can be used to colorize the output of a pipe.

Module usage
------------

    >>> from grec import Matcher
    >>> m = Matcher()
    >>> m.add_pattern('ERROR', 'red')
    >>> m.add_pattern('WARN', 'yellow')
    >>> print m.match('ERROR WARN INFO')
    ERROR WARN INFO  (with color)

TODO
----

* Provide a way to colorize only groups in regular expression
* Add support for attributes like blinking
* Add support for only changing background color from CLI
* Python 3 support
