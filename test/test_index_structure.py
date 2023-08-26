import pytest
from dbms.engine import ordered_dictionary

@pytest.fixture
def od():
    return ordered_dictionary.OrderedDictionary()

# OrderedDictionary is initialized correctly
def test_size_is_zero(od):
    assert od.size == 0, "size not initialized to 0"

def test_hashmap_len_zero(od):
    assert len(od.hashmap) == 0, "hashmap length should be 0."

def test_keys_list_zero(od):
    assert len(od.keys) == 0, "list of keys length should be 0."
