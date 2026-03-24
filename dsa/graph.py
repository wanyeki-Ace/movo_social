"""
Graph module for Movo social network.

Implements an adjacency-list directed graph to model follow relationships.
Used for BFS-based "people you may know" recommendations.

Time complexities:
  - add_user:       O(1)
  - add_follow:     O(1)
  - remove_follow:  O(1)
  - bfs_recommendations: O(V + E)  where V = users, E = follow edges
"""
from collections import deque


class Graph:
    """
    Directed adjacency-list graph representing the social network.

    Each node is a user_id (int).
    Each directed edge (u -> v) means user u follows user v.
    """

    def __init__(self):
        # Maps user_id -> set of user_ids that this user follows
        self.adjacency_list: dict[int, set] = {}

    # ------------------------------------------------------------------
    # Mutation helpers
    # ------------------------------------------------------------------

    def add_user(self, user_id: int) -> None:
        """Ensure a node exists for user_id."""
        if user_id not in self.adjacency_list:
            self.adjacency_list[user_id] = set()

    def add_follow(self, follower_id: int, following_id: int) -> None:
        """Add directed edge follower -> following."""
        self.add_user(follower_id)
        self.add_user(following_id)
        self.adjacency_list[follower_id].add(following_id)

    def remove_follow(self, follower_id: int, following_id: int) -> None:
        """Remove directed edge follower -> following (if it exists)."""
        if follower_id in self.adjacency_list:
            self.adjacency_list[follower_id].discard(following_id)

    def get_following(self, user_id: int) -> set:
        """Return the set of user_ids that user_id follows."""
        return self.adjacency_list.get(user_id, set())

    # ------------------------------------------------------------------
    # BFS recommendation engine
    # ------------------------------------------------------------------

    def bfs_recommendations(self, user_id: int, max_recommendations: int = 10) -> list:
        """
        BFS (Breadth-First Search) traversal to find FOAF recommendations.

        Algorithm
        ---------
        Level 0: the source user
        Level 1: users the source follows  (already known — skip as candidates)
        Level 2: users followed by Level-1 users (FOAF candidates)

        A candidate's *score* equals the number of Level-1 users who also
        follow them — i.e. how many mutual connections endorse them.

        Returns
        -------
        List of (user_id, score) tuples, sorted by score descending,
        limited to max_recommendations entries.

        Complexity: O(V + E) — each node and edge visited at most once.
        """
        if user_id not in self.adjacency_list:
            return []

        already_following = self.get_following(user_id)
        visited = {user_id} | already_following

        # BFS queue holds direct followings (level-1 nodes)
        queue = deque(already_following)

        candidate_scores: dict[int, int] = {}

        while queue:
            current = queue.popleft()

            # Level-1 nodes: the users that the source already follows.
            # Their followings are the FOAF (Level-2) candidates.
            # Score each candidate by how many Level-1 nodes endorse them.
            for neighbor in self.get_following(current):
                if neighbor not in visited:
                    candidate_scores[neighbor] = candidate_scores.get(neighbor, 0) + 1

        sorted_candidates = sorted(candidate_scores.items(), key=lambda x: x[1], reverse=True)
        return sorted_candidates[:max_recommendations]

    # ------------------------------------------------------------------
    # Utility
    # ------------------------------------------------------------------

    def get_mutual_follows(self, user1_id: int, user2_id: int) -> set:
        """
        Return the set of user_ids that both user1 and user2 follow.
        Useful for displaying "followed by people you follow" on profiles.
        """
        return self.get_following(user1_id) & self.get_following(user2_id)
