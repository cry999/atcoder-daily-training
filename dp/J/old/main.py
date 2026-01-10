import sys

sys.setrecursionlimit(10**7)


N = int(input())
(*a,) = map(int, input().split())


states = [[[-1] * (N + 1) for _ in range(N + 1)] for _ in range(N + 1)]


def dfs(n1: int, n2: int, n3: int) -> float:
    global states

    if n1 == n2 == n3 == 0:
        states[n1][n2][n3] = 0
        return states[n1][n2][n3]
    if n2 == n3 == 0 and n1 == 1:
        states[n1][n2][n3] = N
        return states[n1][n2][n3]

    if states[n1][n2][n3] != -1:
        return states[n1][n2][n3]

    ans = 0
    if n1 > 0:
        ans += dfs(n1 - 1, n2, n3) * n1
    if n2 > 0:
        ans += dfs(n1 + 1, n2 - 1, n3) * n2
    if n3 > 0:
        ans += dfs(n1, n2 + 1, n3 - 1) * n3
    ans += N
    ans /= n1 + n2 + n3

    states[n1][n2][n3] = ans
    return states[n1][n2][n3]


print(dfs(*[a.count(i + 1) for i in range(3)]))
