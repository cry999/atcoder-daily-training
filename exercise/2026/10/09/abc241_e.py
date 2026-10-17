# >>> atcoder-stat >>>
# started_at  = 2026-10-09T18:42:39+09:00
# solved_at   = 2026-10-09T19:00:24+09:00
# duration_ms = 1065112
# ac          = true
# editorial   = false
# knowledge   = 3
# translation = 3
# complexity  = 3
# impl        = 3
# verify      = 3
# <<< atcoder-stat <<<
N, K = map(int, input().split())
(*A,) = map(int, input().split())

M = K.bit_length()
# dp[i][j] := 皿にあるアメの個数を N で割ったあまりが i の状態からスタートして 2^j 回操作を行った時の皿のアメの個数
dp = [[0] * (M + 1) for _ in range(N)]
for x in range(N):
    dp[x][0] = A[x]
print(f"[DEBUG] {dp=}")

for j in range(1, M + 1):
    for x in range(N):
        dp[x][j] = dp[x][j - 1] + dp[(x + dp[x][j - 1]) % N][j - 1]
print(f"[DEBUG] {dp=}")

ans = 0
for j in range(M + 1):
    if (K >> j) & 1:
        ans += dp[ans % N][j]
print(ans)
