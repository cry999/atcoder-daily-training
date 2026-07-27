# >>> atcoder-stat >>>
# started_at  = 2026-07-27T22:27:58+09:00
# solved_at   = 2026-07-27T22:36:24+09:00
# duration_ms = 506513
# target_ms   = 900000
# ac          = true
# editorial   = false
# knowledge   = 3
# translation = 3
# complexity  = 3
# impl        = 3
# verify      = 3
# <<< atcoder-stat <<<
T = input()
L = len(T)

N = int(input())
strings = []
for _ in range(N):
    _, *S = input().split()
    strings.append(S)

INF = 10**18
# dp[i] := S を文字列 T の i 文字目まで一致させるのに必要なコスト
dp = [INF] * (L + 1)
dp[0] = 0
for ss in strings:
    ndp = dp[:]
    for s in ss:
        n = len(s)
        for i in range(L - n + 1):
            if T[i : i + n] != s:
                continue
            ndp[i + n] = min(ndp[i + n], dp[i] + 1)

    print(f"[DEBUG] {ndp=}")
    dp = ndp

print(dp[L] if dp[L] < INF else -1)
