"""
MaxHeap module for Movo trending-posts ranking.

Implements a binary max-heap from scratch (no heapq).
Used to efficiently find the top-N posts by engagement score.

Time complexities:
  - push:   O(log n)
  - pop:    O(log n)
  - peek:   O(1)
  - get_trending_posts: O(m log m) where m = total posts
"""
import time as _time


class MaxHeap:
    """
    Binary max-heap storing (priority, data) pairs.

    The heap property: every parent's priority >= its children's priority.
    Internal storage: a flat list (1-indexed arithmetic via 0-indexed offsets).

    Index relationships for node at index i:
      parent:       (i - 1) // 2
      left child:   2*i + 1
      right child:  2*i + 2
    """

    def __init__(self):
        # Each element is (priority, data)
        self.heap: list = []

    def __len__(self) -> int:
        return len(self.heap)

    def push(self, priority: float, data) -> None:
        """Insert an item with given priority. O(log n)."""
        self.heap.append((priority, data))
        self._heapify_up(len(self.heap) - 1)

    def pop(self):
        """Remove and return the (priority, data) with maximum priority. O(log n)."""
        if not self.heap:
            raise IndexError("pop from empty heap")
        # Swap root with last element, shrink, then restore heap property
        self._swap(0, len(self.heap) - 1)
        item = self.heap.pop()
        if self.heap:
            self._heapify_down(0)
        return item

    def peek(self):
        """Return (priority, data) with maximum priority without removing. O(1)."""
        if not self.heap:
            raise IndexError("peek at empty heap")
        return self.heap[0]

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _swap(self, i: int, j: int) -> None:
        self.heap[i], self.heap[j] = self.heap[j], self.heap[i]

    def _heapify_up(self, index: int) -> None:
        """Bubble the element at *index* up until heap property is restored."""
        while index > 0:
            parent = (index - 1) // 2
            if self.heap[index][0] > self.heap[parent][0]:
                self._swap(index, parent)
                index = parent
            else:
                break

    def _heapify_down(self, index: int) -> None:
        """Push the element at *index* down until heap property is restored."""
        size = len(self.heap)
        while True:
            largest = index
            left = 2 * index + 1
            right = 2 * index + 2

            if left < size and self.heap[left][0] > self.heap[largest][0]:
                largest = left
            if right < size and self.heap[right][0] > self.heap[largest][0]:
                largest = right

            if largest != index:
                self._swap(index, largest)
                index = largest
            else:
                break

    # ------------------------------------------------------------------
    # Class-level convenience method
    # ------------------------------------------------------------------

    @classmethod
    def get_trending_posts(cls, posts, n: int = 10) -> list:
        """
        Return the top-n Post objects ranked by engagement score.

        Engagement score = likes + comments*2 + recency_bonus
          recency_bonus  = max(0, 48 - hours_since_post) * 2
          (newer posts within 48 hours receive a bonus that decays linearly)

        Uses a max-heap: all m posts are pushed in O(m log m), then
        the top n are popped in O(n log m).  Total: O(m log m).
        """
        heap = cls()
        for post in posts:
            score = post.engagement_score()
            heap.push(score, post)

        result = []
        count = min(n, len(heap))
        for _ in range(count):
            _, post = heap.pop()
            result.append(post)
        return result
