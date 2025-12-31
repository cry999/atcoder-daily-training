import sys

sys.setrecursionlimit(10**7)


N = int(input())

memo = {}


def dfs(n: int) -> int:
    global memo

    if n < 2:
        return 0

    if n in memo:
        return memo[n]

    if n % 2 == 0:
        memo[n] = 2 * dfs(n // 2) + n
    else:
        memo[n] = dfs((n + 1) // 2) + dfs((n - 1) // 2) + n

    return memo[n]


print(dfs(N))
