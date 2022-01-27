import pytest

import data

def test_chunk():
    # Divide iterable into chunks.
    chunked_8_4 = list(data.chunk(range(8), 4))
    assert chunked_8_4 == [(0, 1, 2, 3), (4, 5, 6, 7)]

    # If there's extra data, there will be a smaller chunk.
    chunked_10_4 = list(data.chunk(range(10), 4))
    assert chunked_10_4 == [(0, 1, 2, 3), (4, 5, 6, 7), (8, 9)]

    # Chunks may be smaller than maxsize if there is not enough in iterable.
    chunked_5_20 = list(data.chunk(range(5), 20))
    assert chunked_5_20 == [(0, 1, 2, 3, 4)]


def test_listionary():
    # Basic behavior
    l1 = data.Listionary()

    l1.append("auto_list", 8)
    assert l1 == {"auto_list": [8]}

    l1["manual_list"] = [8]
    assert l1 == {"auto_list": [8], "manual_list": [8]}

    # ...but you can't directly assign non-list values.
    l2 = data.Listionary()
    l2["coerce_list"] = "spam"
    assert l2 == {"coerce_list": ['s', 'p', 'a', 'm']}

    # You can also remove items from a list in one step
    l2.remove("coerce_list", 's')
    assert l2 == {"coerce_list": ['p', 'a', 'm']}


    # You can also disable error smoothing
    l3 = data.Listionary()
    with pytest.raises(KeyError):
        l3.append("missing", 8, create_needed=False)