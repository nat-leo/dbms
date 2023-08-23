class Hashmap:
    def __init__(self) -> None:
        self.size = 0
        self.pairs = {}

    def insert(self, key, value):
        self.pairs[key] = value
        self.size += 1

    def delete(self, key):
        del self.pairs[key]
        self.size -= 1

    def clear(self):
        self.size = 0
        self.pairs = {}
