import pytest
import ordered_dictionary

@pytest.fixture
def init():
    pass

# ordered dictionary has three attributes: a hashmap for storing key-list of 
# addresses pairs, a sorted list for storing keys currently in the hashmap (
# we do this for quick range accesses), and a size attribute for the the 
# number of rows currently in said index structure.
def ordered_dict_correctly_built():
    # assert len(list) == size == the sum of len(addresses list) in the hashmap
    # (the length of the list which corresponds to value in the key-value pairs):

    # assert list is always sorted:
    pass

# ordered dicctionary has two data structures. Adding a new row should update 
# both the hashmap and the list.
def insert_updates_both_list_and_hashmap_test():
    od = ordered_dictionary.OrderedDictionary()
    ordered_dict_correctly_built()
    od.insert(("123 Main Street", 1500, "55113", 3, 2))
    ordered_dict_correctly_built()
