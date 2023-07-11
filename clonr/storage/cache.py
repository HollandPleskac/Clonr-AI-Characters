from collections import OrderedDict


class Cache:
    def __init__(self, max_size: int = 100_000):
        self.max_size = max_size
        self._d = OrderedDict()

    def set(self, key, value):
        if self.max_size <= len(self._d) and key not in self._d:
            self._d.popitem(last=False)
        self._d[key] = value
        self._d.move_to_end(key)

    def get(self, key):
        if key in self._d:
            self._d.move_to_end(key)
            return self._d[key]

    def delete(self, key):
        if key in self._d:
            self._d.pop(key)

    def increment(self, key):
        if key in self._d:
            self._d[key] += 1
