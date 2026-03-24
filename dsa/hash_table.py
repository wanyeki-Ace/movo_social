"""
HashTable module for Movo — custom implementation with chaining.

Used in views for O(1) average-time lookup of "did the current user
like this post?" without repeated database queries.

Time complexities (average / worst case):
  - set:    O(1) / O(n)
  - get:    O(1) / O(n)
  - delete: O(1) / O(n)

Collision resolution: separate chaining (each bucket holds a list of
key-value pairs).  Load-factor-based resizing keeps chains short.
"""


class HashTable:
    """
    Hash table with separate chaining and polynomial rolling hash.

    Automatically resizes (doubles capacity) when load factor > 0.75.
    """

    _LOAD_FACTOR_THRESHOLD = 0.75

    def __init__(self, capacity: int = 64):
        self._capacity = capacity
        self._size = 0
        # Each bucket is a list of [key, value] pairs (chaining)
        self._buckets: list[list] = [[] for _ in range(self._capacity)]

    # ------------------------------------------------------------------
    # Hashing
    # ------------------------------------------------------------------

    def _hash(self, key: str) -> int:
        """
        Polynomial rolling hash (similar to Java's String.hashCode).

        hash = sum(ord(char) * BASE^i) mod capacity
        BASE = 31 (prime, good for lowercase ASCII)
        """
        BASE = 31
        MOD = self._capacity
        h = 0
        for char in str(key):
            h = (h * BASE + ord(char)) % MOD
        return h

    # ------------------------------------------------------------------
    # Core operations
    # ------------------------------------------------------------------

    def set(self, key, value) -> None:
        """Insert or update key -> value. O(1) amortised."""
        index = self._hash(key)
        bucket = self._buckets[index]
        for pair in bucket:
            if pair[0] == key:
                pair[1] = value
                return
        bucket.append([key, value])
        self._size += 1
        if self._size / self._capacity > self._LOAD_FACTOR_THRESHOLD:
            self._resize()

    def get(self, key, default=None):
        """Return value for key, or default if not present. O(1) amortised."""
        index = self._hash(key)
        for pair in self._buckets[index]:
            if pair[0] == key:
                return pair[1]
        return default

    def delete(self, key) -> bool:
        """Remove key from the table. Returns True if found. O(1) amortised."""
        index = self._hash(key)
        bucket = self._buckets[index]
        for i, pair in enumerate(bucket):
            if pair[0] == key:
                bucket.pop(i)
                self._size -= 1
                return True
        return False

    def __contains__(self, key) -> bool:
        """Support 'key in ht' syntax. O(1) amortised."""
        index = self._hash(key)
        for pair in self._buckets[index]:
            if pair[0] == key:
                return True
        return False

    def __len__(self) -> int:
        return self._size

    # ------------------------------------------------------------------
    # Resizing
    # ------------------------------------------------------------------

    def _resize(self) -> None:
        """Double capacity and rehash all entries. O(n)."""
        old_buckets = self._buckets
        self._capacity *= 2
        self._size = 0
        self._buckets = [[] for _ in range(self._capacity)]
        for bucket in old_buckets:
            for key, value in bucket:
                self.set(key, value)
