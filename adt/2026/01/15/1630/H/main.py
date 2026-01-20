import math

N, M = map(int, input().split())

towns = [tuple(map(int, input().split())) for _ in range(N)]
boosters = [tuple(map(int, input().split())) for _ in range(M)]


def pos(i: int) -> tuple[int, int]:
    # 最初と最後は原点なので
    if 0 <= i < N:
        # 街
        return towns[i]
    else:
        # ブースター
        return boosters[i - N]


def dist(i: int, j: int) -> float:
    xi, yi = pos(i)
    xj, yj = pos(j)
    return math.sqrt((xi - xj) ** 2 + (yi - yj) ** 2)


# dp[i][bit] := 通過済みの街・ブースターが bit の状態である時に街 or ブースター i の場所にいる
# 場合の最小コスト
dp = [[float("inf")] * (1 << (N + M)) for _ in range(N + M)]
dp[0][1] = 0  # スタート
for i in range(N + M):
    x, y = pos(i)
    dp[i][1 << i] = math.sqrt(x**2 + y**2)


for state in range(1 << N << M):
    for cur in range(N + M):
        if state & (1 << cur) == 0:
            # not visited
            continue

        for nxt in range(N + M):
            if state & (1 << nxt):
                # already visited
                continue
            # 上位 M 桁がブースターの通過状況。
            # なので、上位 M 桁の 1 が立っている個数が速度になる。
            v = 1 << (state >> N).bit_count()
            nxt_state = state | (1 << nxt)
            dp[nxt][nxt_state] = min(
                dp[nxt][nxt_state],
                dp[cur][state] + dist(cur, nxt) / v,
            )

ans = float("inf")
for booster_state in range(1 << M):
    v = 1 << booster_state.bit_count()
    state = (booster_state << N) | ((1 << N) - 1)
    for j in range(N + M):
        x, y = pos(j)
        ans = min(ans, dp[j][state] + math.sqrt(x**2 + y**2) / v)
print(f"{ans:.10f}")
