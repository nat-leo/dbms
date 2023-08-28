class Node:
    def __init__(self, val, left=None, right=None) -> None:
        self.val = val
        self.left = left
        self.right = right

    def __str__(self) -> str:
        return self.left.__repr__() + " " + self.right.__repr__() + " " + self.val

class BinarySearchTree:
    def __init__(self) -> None:
        self.root = None
        self.size = 1

    def __repr__(self) -> str:
        return self.root.__repr__()

    def search(self):
        pass

    def insert(self, val):
        pass

    def delete(self, val):
        pass