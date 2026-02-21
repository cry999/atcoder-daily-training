from bisect import bisect_left as b

N, M = map(int, input().split())

securities = sorted(
    [tuple(map(int, input().split())) for _ in range(M)],
    key=lambda x: (x[0], -x[1]),
)

# dp[x] := x 人でカバーできる範囲の最右端 + 1 ([l, r))
# dp[x] := max(dp[x], r[i]) if l[i] <= dp[x-1]
dp = [0] * (M + 1)
dp[0] = 1
hi = 0

for l, r in securities:
    # TODO: 更新範囲を絞る
    # NOTE: 下からだと、dp[i] を更新した結果が dp[i+1] に悪影響を与える。
    lx = b(dp, l, hi=hi)
    if dp[lx] < l:
        continue
    hi = max(hi, lx + 1)
    dp[lx + 1] = max(dp[lx + 1], r + 1)

ans = -1
for x, n in enumerate(dp):
    if n == N + 1:
        ans = x
        break
# print(*dp)
print(ans)
