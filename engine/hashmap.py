class Hashmap:
    def __init__(self) -> None:
        self.size = 0
        self.pairs = {}

    def insert(self, key, value):
        if key in self.pairs:
            self.pairs[key].append(value)
        else:
            self.pairs[key] = [value]
        self.size += 1

    def delete(self, key):
        self.size -= len(self.pairs[key])
        del self.pairs[key]

    def clear(self):
        self.size = 0
        self.pairs = {}
