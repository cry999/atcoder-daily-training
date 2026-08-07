# >>> atcoder-stat >>>
# started_at  = 2026-08-04T07:47:21+09:00
# solved_at   = 2026-08-04T07:54:40+09:00
# duration_ms = 439327
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
bags = []
for _ in range(N):
    _, *strings = input().split()
    bags.append(strings)


INF = 10**18
# dp[l] = T[:l] を作るのに必要な最小コスト
dp = [INF] * (L + 1)
dp[0] = 0

for i in range(N):
    bag = bags[i]

    ndp = [x for x in dp]
    for s in bag:
        l = len(s)
        for i in range(L - l, -1, -1):
            if T[i : i + l] != s:
                continue
            ndp[i + l] = min(ndp[i + l], dp[i] + 1)
    dp[:] = ndp[:]

print(dp[L] if dp[L] < INF else -1)
