# >>> atcoder-stat >>>
# started_at  = 2026-10-02T09:38:13+09:00
# solved_at   = 2026-10-02T10:01:21+09:00
# duration_ms = 1388121
# ac          = true
# editorial   = true
# knowledge   = 3
# translation = 2
# complexity  = 3
# impl        = 2
# verify      = 3
# <<< atcoder-stat <<<
MOD = 998244353


N = input()

M = 1 << 10
# dp[s][r][less]
# s: 0~9 の数字の使用状況
# r: 3 で割ったあまり
# less: N より小さいことが確定しているかどうか
dp = [[[0] * 2 for _ in range(3)] for _ in range(M)]
dp[0][0][0] = 1

for i in range(len(N)):
    n = int(N[i])
    ndp = [[[0] * 2 for _ in range(3)] for _ in range(M)]

    for s in range(M):
        for r in range(3):
            for less in range(2):
                if dp[s][r][less] == 0:
                    continue

                limit = 9 if less else n
                for d in range(limit + 1):
                    ns = s | (1 << d)
                    if s == 0 and d == 0:
                        ns = 0
                    nr = (10 * r + d) % 3
                    nless = less or d < n

                    ndp[ns][nr][nless] += dp[s][r][less]
                    ndp[ns][nr][nless] %= MOD

    dp = ndp

ans = 0
for s in range(2, M):
    for r in range(3):
        satisfied = 0
        satisfied += s.bit_count() == 3
        satisfied += s & (1 << 3) != 0
        satisfied += r == 0
        if satisfied == 1:
            ans += sum(dp[s][r])
    ans %= MOD

print(ans)
