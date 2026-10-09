# >>> atcoder-stat >>>
# started_at  = 2026-10-07T11:12:16+09:00
# solved_at   = 2026-10-07T19:17:10+09:00
# duration_ms = 29094548
# ac          = true
# editorial   = false
# knowledge   = 3
# translation = 3
# complexity  = 3
# impl        = 3
# verify      = 3
# <<< atcoder-stat <<<
N, Q = map(int, input().split())
X = [0] + list(map(int, input().split()))

L, R, A, B = [], [], [], []
for _ in range(N):
    l, r, a, b = map(int, input().split())
    L.append(l)
    R.append(r)
    A.append(a)
    B.append(b)

(*C,) = map(int, input().split())

INF = float("inf")
# dp[n][j] := n 人で地点 j に到達するのにかかる最小費用
dp = [[INF] * (N + 1) for _ in range(N + 1)]
dp[0][0] = 0
for n in range(N):
    for i in range(n, N):
        if dp[n][i] == INF:
            continue
        for k in range(L[i], min(R[i], N - i) + 1):
            dp[n + 1][i + k] = min(
                dp[n + 1][i + k], dp[n][i] + A[i] * (X[i + k] - X[i]) + B[i]
            )

if all(dp[n][N] == INF for n in range(N + 1)):
    print("\n".join(["-1"] * Q))
else:
    ans = []
    for c in C:
        ans.append(INF)
        for n in range(1, N + 1):
            ans[-1] = min(ans[-1], dp[n][N] + n * c)
    print("\n".join(map(str, ans)))
