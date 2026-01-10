N = int(input())
(*a,) = map(int, input().split())

N1, N2, N3 = [a.count(i + 1) for i in range(3)]
dp = [[[-1] * (N + 1) for _ in range(N + 1)] for _ in range(N + 1)]
dp[N1][N2][N3] = 1


def ok(n1: int, n2: int, n3: int) -> bool:
    """n1, n2, n3 があり得る状態かを判定する"""
    if n3 > N3:
        return False
    if n3 == N3 and n2 > N2:
        return False
    if n3 == N3 and n2 == N2 and n1 > N1:
        return False
    return 0 <= n1 and 0 <= n2 and 0 <= n3 and n3 + n2 + n1 <= N


def dfs(n1: int, n2: int, n3: int) -> float:
    if dp[n1][n2][n3] != -1:
        return dp[n1][n2][n3]

    dp[n1][n2][n3] = 0
    if ok(n1 + 1, n2, n3):
        # 1 の皿から 0 の皿へ
        dp[n1][n2][n3] += (n1 + 1) * dfs(n1 + 1, n2, n3) / N
    if ok(n1 - 1, n2 + 1, n3):
        # 2 の皿から 1 の皿へ
        dp[n1][n2][n3] += (n2 + 1) * dfs(n1 - 1, n2 + 1, n3) / N
    if ok(n1, n2 - 1, n3 + 1):
        # 3 の皿から 2 の皿へ
        dp[n1][n2][n3] += (n3 + 1) * dfs(n1, n2 - 1, n3 + 1) / N

    if n1 + n2 + n3:
        dp[n1][n2][n3] *= N / (n1 + n2 + n3)
    return dp[n1][n2][n3]


dfs(0, 0, 0)

ans = 0
for n1 in range(N + 1):
    for n2 in range(N + 1):
        for n3 in range(N + 1):
            if dp[n1][n2][n3] == -1:
                continue
            ans += dp[n1][n2][n3]
print(ans-1)
