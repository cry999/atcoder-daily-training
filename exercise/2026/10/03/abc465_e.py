# >>> atcoder-stat >>>
# started_at  = 2026-10-03T11:55:01+09:00
# solved_at   = 2026-10-03T12:02:24+09:00
# duration_ms = 443434
# ac          = true
# editorial   = false
# knowledge   = 3
# translation = 3
# complexity  = 3
# impl        = 3
# verify      = 3
# <<< atcoder-stat <<<
MOD = 998244353

N = input()
M = 1 << 10
R = 3
# dp[s][r][less] :=
# s: 0 ~ 9 の利用状況
# r: 3 で割ったあまり
# less: N より小さいかどうかが確定
dp = [[[0] * 2 for _ in range(R)] for _ in range(M)]
dp[0][0][0] = 1

for c in N:
    n = int(c)

    ndp = [[[0] * 2 for _ in range(R)] for _ in range(M)]
    for s in range(M):
        for r in range(R):
            for less in range(2):
                if dp[s][r][less] == 0:
                    continue

                limit = 9 if less else n
                for d in range(limit + 1):
                    ns = s | (1 << d)
                    if d == 0 and s == 0:
                        ns = 0
                    nr = (r * 10 + d) % R
                    nless = less or d < n

                    ndp[ns][nr][nless] += dp[s][r][less]
                    ndp[ns][nr][nless] %= MOD
    dp = ndp

ans = 0
for s in range(1, M):
    for r in range(R):
        satisfied = 0
        satisfied += s.bit_count() == 3
        satisfied += s & (1 << 3) != 0
        satisfied += r == 0

        if satisfied == 1:
            ans += sum(dp[s][r])
            ans %= MOD
print(ans)
