# Data structures


def chunk(iterable, maxsize):
    """A generator that yields lists of size `maxsize` containing the results of iterable `it`.

    Args:
        iterable: An iterable to split into chunks
        maxsize (int): Max size of chunks

    Yields:
        lists of size [1, maxsize]

    >>> list(chunk(range(10), 4))
    [(0, 1, 2, 3), (4, 5, 6, 7), (8, 9)]
    """
    from itertools import islice
    iter_it = iter(iterable)
    yield from iter(lambda: tuple(islice(iter_it, maxsize)), ())


def flatList(lst):
    """Turn a (one-level) nested list into one list.
    >>> flatList([[1, 2], [3, 4]])
    [1, 2, 3, 4]
    """
    return [item for sublist in lst for item in sublist]


class Listionary(dict):
    """A special dictionary whose values are exclusively lists. 
    Helper functions included to simplify key: list data structures.
    """

    def __setitem__(self, key, value):
        if type(value) is list:
            super().__setitem__(key, value)
        elif "__len__" in dir(value) and len(value) > 1:
            super().__setitem__(key, [m for m in value])
        else:
            super().__setitem__(key, [value])

    def append(self, key, value, create_needed=True):
        """Append a value to a key's list.

        If create_needed is set to False, this will error if key is missing.
        Otherwise, key will be created automatically.
        """
        if create_needed:
            self[key] = self.get(key, []) + [value]
        else:
            self[key].append(value)
        return self[key]

    def remove(self, key, value):
        self[key].remove(value)
        return self[key]


class Dummy():
    """Substitute this for other pieces of code for testing purposes. Doesn't error out.

    >>> d = Dummy()
    >>> type(d.fish)     # gives another dummy 
    <class 'data.Dummy'>
    >>> type(d(3))   # gives another dummy
    <class 'data.Dummy'>
    >>> type(d.get(8))   # gives another dummy
    <class 'data.Dummy'>
    >>> type(d[42])      # gives another dummy
    <class 'data.Dummy'>
    """

    def __getattribute__(self, name):
        return Dummy()

    def __getitem__(self, name):
        return Dummy()

    def __call__(self, *args, **kwargs):
        return Dummy()


class AttrDump():
    """Holds arbitrary attributes. Example:

    >>> a = AttrDump
    >>> a.fish = 'fish'
    >>> a.fish
    'fish'

    "Okay, so obviously THIS one is useless, right?"
    """
    pass


def crawlApi(value, mykey="Root", indent=0):
    """Prints out an inspection of an API output to summarize the data structure."""

    indentstr = " " * indent * 2
    typestr = "[{}]".format(type(value))

    if isinstance(value, dict):
        print(indentstr, mykey, typestr, "...")
        for key in value.keys():
            crawlApi(value[key], key, indent + 1)
    elif isinstance(value, list):
        print(indentstr, mykey, typestr, "...")
        if len(value) > 0:
            crawlApi(value[0], mykey, indent + 1)
    else:
        print(indentstr, mykey, typestr, repr(value)[:128])
