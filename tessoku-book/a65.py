import sys


sys.setrecursionlimit(10**6)

N = int(input())
*A, = map(int, input().split())

tree = [[] for _ in range(N+1)]

for i in range(2, N+1):
    tree[A[i-2]].append(i)

dp = [0] * (N+1)


def dfs(v: int) -> int:
    if dp[v] != 0:
        return dp[v]
    dp[v] = sum(dfs(nv) for nv in tree[v])
    return dp[v] + 1


dp[1] = dfs(1)-1
print(*dp[1:])
