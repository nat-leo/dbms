class Hashmap:
    def __init__(self) -> None:
        self.map = {} # maps are key value pairs, where the value is a list.
        self.size = 0

    def __repr__(self) -> str:
        pass

    def search(self, key):
        return self.map[key]

    def insert(self, key, val: int):
        # value MUST be an int.
        if type(val) is not int: 
            raise ValueError(f"val {val} of type {type(val)} not an int")
        
        if key in self.map:
            self.map[key].append(val) # maps are key, list pairs b/c keys are not unique.
        else:
            self.map[key] = [val]

        self.size += 1
        

    def delete(self, key, value):
        pass