import sys

sys.setrecursionlimit(10**6)


N, K = map(int, input().split())


a = [-1] * N


def dfs(s: int = 0, i: int = 1):
    if i == N:
        if (K - s) % N == 0:
            a[-1] = (K - s) // N
            print(*a)
        return

    for j in range((K - s) // i + 1):
        a[i - 1] = j
        dfs(s + i * j, i + 1)

    return


dfs()
