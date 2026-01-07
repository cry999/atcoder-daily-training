import sys

sys.setrecursionlimit(10**7)

MOD = 10**9 + 7


N = int(input())
tree = [[] for _ in range(N + 1)]

for _ in range(N - 1):
    x, y = map(int, input().split())
    tree[x].append(y)
    tree[y].append(x)


def dfs(u: int, parent: int) -> tuple[int, int]:
    black, white = 1, 1
    for v in tree[u]:
        if v == parent:
            continue
        nb, nw = dfs(v, u)

        black *= nw
        black %= MOD

        white *= nb + nw
        white %= MOD

    return black, white


print(sum(dfs(1, -1)) % MOD)
