from itertools import accumulate, groupby

INF = 10**18

N, M = map(int, input().split())
cost = [0] * N
value = [0] * N
for i in range(N):
    cost[i], value[i] = map(int, input().split())

index = sorted(range(N), key=lambda i: cost[i], reverse=True)
dp = [[-INF] * (M + 1) for _ in range(N + 1)]
dp[0][0] = 0

ans = [0] * (M + 1)
total_value = sum(value)
free_value = total_value  # コストを支払わずに取得できる価値

# コストごとにグループ化
g = [(c, list(gg)) for c, gg in groupby(index, key=lambda i: cost[i])]

# g[0][0] を超える値引きの場合は、全て無料になる
for j in range(g[0][0], M + 1):
    ans[j] = total_value

prev = M + 1
count = 0

for i, (c, indexes) in enumerate(g):
    if c == 0:
        break

    d = prev - c
    for k in range(count):
        shift = (k + 1) * d
        if shift > M:
            dp[k + 1] = [-INF] * (M + 1)
        else:
            dp[k + 1] = [-INF] * shift + dp[k + 1][: M + 1 - shift]

    for j in indexes:
        count += 1
        free_value -= value[j]

        for k in range(count, 0, -1):
            cur = dp[k]
            old = dp[k - 1]
            for m in range(M + 1):
                cur[m] = max(cur[m], old[m] + value[j])

    next_cost = g[i + 1][0] if i + 1 < len(g) else 0
    best = [0] * (c - next_cost)
    for k in range(count):
        max_value = list(accumulate(dp[k + 1], max))
        for d in range(next_cost, c):
            if M - (k + 1) * (c - d) >= 0:
                best[d - next_cost] = max(
                    best[d - next_cost], max_value[M - (k + 1) * (c - d)]
                )
    for d in range(next_cost, c):
        ans[d] = max(ans[d], best[d - next_cost] + free_value)

    prev = c

print(*ans, sep="\n")
