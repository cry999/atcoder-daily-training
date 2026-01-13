N, K, P = map(int, input().split())

# dp[j] := i 番目までの開発案を採用して、パラメータの状態を j にするときの最小コスト。
# j は P 進数で K 桁。各桁がパラメータの値を表現する。
dp = [float("inf")] * ((P + 1) ** K + 1)
dp[0] = 0

develops = [tuple(map(int, input().split())) for _ in range(N)]


def next_state(state: int, diffs: tuple[int, ...]) -> int:
    next_state = 0
    for i in range(K):
        param = (state // ((P + 1) ** i)) % (P + 1)
        param = min(P, param + diffs[i])
        next_state += param * ((P + 1) ** i)
    return next_state


for i in range(N):
    cost, *a = develops[i]

    for j in range((P + 1) ** K - 1, -1, -1):
        # 開発状態が全てのパラメータが最大になっている時 ((P+1)**K) は
        # それ以上開発してもコストが上がるだけで無意味なので無視する。
        if dp[j] == float("inf"):
            continue

        nj = next_state(j, a)
        dp[nj] = min(dp[nj], dp[j] + cost)

ans = dp[next_state(0, (P,) * K)]
if ans == float("inf"):
    print(-1)
else:
    print(ans)
