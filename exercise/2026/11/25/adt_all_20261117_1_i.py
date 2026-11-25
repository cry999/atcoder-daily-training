# >>> atcoder-stat >>>
# started_at  = 2026-11-25T03:31:36+09:00
# solved_at   = 2026-11-25T10:05:11+09:00
# duration_ms = 23615583
# ac          = true
# editorial   = true
# knowledge   = 1
# translation = 1
# complexity  = 1
# impl        = 1
# verify      = 1
# <<< atcoder-stat <<<
from bisect import bisect_left

INF = 10**18
N, K, X = map(int, input().split())
(*T,) = map(int, input().split())

# events[i] := t
events = sorted({t + k * X for t in T for k in range(N + 1)})
E = len(events)

# dp[i][j] := i 番目までのイベントを処理してトータルで j 個の商品を出荷した場合の不満どの総和の最小値
dp = [[INF] * (N + 1) for _ in range(E + 1)]
dp[0][0] = 0

print(f"[DEBUG] {T=}")

num_order = 0
for i, t in enumerate(events):
    while num_order < N and T[num_order] <= t:
        num_order += 1

    print(f"[DEBUG] {t=} {num_order=}")

    ni = bisect_left(events, t + X)

    prefix_j = 0
    for j in range(num_order + 1):
        if dp[i][j] == INF:
            continue
        # 何も出荷しない場合
        dp[i + 1][j] = min(dp[i + 1][j], dp[i][j])

        # k 個出荷する場合
        prefix_k = prefix_j
        for k in range(1, K + 1):
            if j + k > num_order:
                break
            prefix_k += T[j + k - 1]
            dissatisfaction = t * k - (prefix_k - prefix_j)
            dp[ni][j + k] = min(dp[ni][j + k], dp[i][j] + dissatisfaction)
            print(f"[DEBUG] {j=} {k=} {dp[ni][j+k]=} {dissatisfaction=}")

        prefix_j += T[j] if j < num_order else 0

    print(f"[DEBUG]    -> {dp[ni]=}")
print(dp[E][N])
