import sys
import functools

sys.setrecursionlimit(10**7)


T = int(input())

for _ in range(T):
    N, M, K = map(int, input().split())
    S = input()

    g = [[] for _ in range(N)]
    for _ in range(M):
        u, v = map(int, input().split())
        g[u - 1].append(v - 1)

    nxt_turn = {"A": "B", "B": "A"}

    @functools.cache
    def dfs(u: int, turn: str = "A", k: int = K):
        if turn == "B" and k == 1:
            for v in g[u]:
                if S[v] == turn:
                    return turn
            return nxt_turn[turn]

        for v in g[u]:
            winner = dfs(v, nxt_turn[turn], k - (turn == "B"))
            if winner == turn:
                return winner
        return nxt_turn[turn]

    if dfs(0) == "A":
        print("Alice")
    else:
        print("Bob")
