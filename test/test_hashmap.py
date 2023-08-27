###############################################################################
# Hashmap Test File
###############################################################################
import pytest
from dbms.engine import hashmap

@pytest.fixture
def h():
    h = hashmap.Hashmap()
    return h

# h accepts key value pairs, where the value is always an integer. 
def test_insert_correct(h):
    h.insert("whale", 0)
    h.insert("bert", 24)
    h.insert("bert", 48)
    assert h.search("bert") == [24, 48], "searches should return a list of ints (said int being the number of bytes away from first byte of the file.)"

# h throws error when the value is not an int, and the error should be
# descriptive and be thrown on a variety of types that aren't ints.
def test_insert_value_is_string(h):
    with pytest.raises(ValueError, match="not an int"):
        h.insert("bert", "not an int")

def test_insert_value_is_float(h):
    with pytest.raises(ValueError, match="not an int"):
        h.insert("bert", 10.0)

def test_insert_value_is_dict(h):
    with pytest.raises(ValueError, match="not an int"):
        h.insert("bert", {})
