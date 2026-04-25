from sys import setrecursionlimit

setrecursionlimit(10**7)


N, Q = map(int, input().split())

over = [-1] * (2 * N + 1)
under = [-1] * (2 * N + 1)

for i in range(1, N + 1):
    under[i] = i + N
    over[i + N] = i

for _ in range(Q):
    c, p = map(int, input().split())

    if under[c] != -1:
        over[under[c]] = -1

    under[c] = p
    over[p] = c


ans = [-1] * (2 * N + 1)


def dfs(c: int) -> int:
    if ans[c] != -1:
        return ans[c]

    if over[c] == -1:
        ans[c] = 0
        return ans[c]

    ans[c] = dfs(over[c]) + 1
    return ans[c]


for i in range(1, 2 * N + 1):
    dfs(i)

print(*ans[N + 1 :])
