=====
Usage
=====

To use grec in a project::

    import grec

The `grec` package exports the `Matcher` class.  To prepare text
colorization, create a new `Matcher` instance and add patterns to it::

    matcher = grec.Matcher()
    matcher.add_pattern('ERROR', 'red')
    matcher.add_pattern('WARN', 'yellow')
    matcher.add_pattern('[0-9]', 'blue', 'white')

This instance is now ready to match for colors in strings passed to
it.  Do it with the `match` method::

    result = matcher.match('ERROR WARN INFO')

The result is an instance of `ColoredString`.  Its `__str__` method
will return a string with ANSI escape codes for all matched colors.
Thus, the instance can simply be printed to show the text with colors
in the terminal.  If no patterns matched the string will be printed
without color.

Another way to match is to use the `match_iter` method of the matcher.
This method takes an iterable and will return an iterator which
returns corresponding `ColoredString` instances for each match of the
passed iterable.

::

    lines = ['WARN 1', 'ERROR 2', 'INFO 3']
    for colored_string in matcher.match_iter(lines):
        print colored_string
