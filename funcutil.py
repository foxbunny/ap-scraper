import functools


def pipe2(f, g):
    """ Pipe two functions

    Example:

        >>> def inc(x):
        ...     return x + 1
        >>> def double(x):
        ...     return x * 2
        >>> incdbl = pipe2(inc, double)
        >>> incdbl(2)
        6
        >>> incdbl(5)
        12
        >>> dblinc = pipe2(double, inc)
        >>> dblinc(2)
        5
        >>> dblinc(5)
        11
    """

    @functools.wraps(f)
    def composed(*args, **kwargs):
        return g(f(*args, **kwargs))

    return composed


def pipe(*fns):
    """ Ppipe 2 or more functions

    Example:

        >>> def inc(x):
        ...     return x + 1
        >>> def double(x):
        ...     return x * 2
        >>> incdblstr = pipe(inc, double, str)
        >>> incdblstr(2)
        '6'
    """
    assert len(fns) >= 2, "There should be 2 or more functions in a pipe"
    return functools.reduce(pipe2, fns)


class Some:
    def __init__(self, x):
        self.x = x

    def map(self, f):
        return Some(f(self.x))

    def flatten(self):
        return self.x

    def __str__(self):
        return "Some(%s)" % self.x


class __Nothing:
    def map(self, fn):
        return Nothing

    def flatten(self):
        return None

    def __str__(self):
        return "Nothing"


Nothing = __Nothing()


def maybe(x):
    """ Return a Nothing if x is None, otherwise Some(x)

    Examples:

        >>> m = maybe(None)
        >>> str(m)
        'Nothing'
        >>> m = m.map(lambda x: x + 1)
        >>> m.flatten()
        >>> m = maybe(2)
        >>> str(m)
        'Some(2)'
        >>> m = m.map(lambda x: x + 1)
        >>> m.flatten()
        3
    """
    if x is None:
        return Nothing
    return Some(x)


def when(pred, fn):
    """ Takes a predicate and a function and returns a function that invokes the 
    original function only when the predicate returns True for the passed 
    argument. If the predicate returns False, the argument is returned as is.

    Example:

        >>> fraction = when(lambda x: x != 0, lambda x: 1 / x)
        >>> fraction(0)
        0
        >>> fraction(2)
        0.5
    """

    def guarded(x):
        if pred(x):
            return fn(x)
        return x

    return guarded


def unless(pred, fn):
    """ Takes a predicate and a function and returns a function that invokes the 
    original function only when the predicate returns False for the passed 
    argument. If the predicate returns True, the argument is returned as is.

    Example:

        >>> stringify = unless(lambda x: x is None, lambda x: str(x))
        >>> stringify(None)
        >>> stringify(12)
        '12'
    """

    def guarded(x):
        if pred(x):
            return x
        return fn(x)

    return guarded


def default(x):
    """ Return a function that takes a single value and returns x if the
    value is None

    Example:

        >>> d = default('')
        >>> d(None)
        ''
        >>> d('foo')
        'foo'
    """
    return lambda y: x if y is None else y


def is_none(x):
    """ Return True if x is None """
    return x is None


def apply_to(val, f):
    """ Apply a function f to a value

    Example:

        >>> apply_to(12, lambda x: x * 2)
        24
    """
    return f(val)


def filter_by(f):
    """ Return a partially applied filter() built-in

    Example:

        >>> f = filter_by(lambda x: x % 2 == 0)
        >>> list(f([1, 2, 3, 4]))
        [2, 4]
    """
    return functools.partial(filter, f)


def map_with(f):
    """ Return a partially applied map() built-in

    Example:

        >>> m = map_with(lambda x: x + 1)
        >>> list(m([1, 2, 3]))
        [2, 3, 4]
    """
    return functools.partial(map, f)


def from_spec(spec):
    """ Given a spec in the form of a dict that maps keys to functions,
    return a function that creates a dict with the same keys as the spec,
    and values that are the result of calling the matching function and
    passing it the argument to the function.

    Example:

        >>> spec = {
        ...   'foo': lambda x: 'foo' + x,
        ...   'bar': lambda x: 'bar' + x,
        ... }
        >>> f = from_spec(spec)
        >>> f('baz')
        {'foo': 'foobaz', 'bar': 'barbaz'}
    """
    def apply_spec(x):
        return {k: v(x) for k, v in spec.items()}
    return apply_spec


def through(f):
    """ Given a function f, return a function that will invoke f with its own
    argument and then return the argument as is """
    def g(x):
        f(x)
        return x
    return g


if __name__ == "__main__":
    import doctest

    doctest.testmod()
