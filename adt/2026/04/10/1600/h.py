N, K = map(int, input().split())

dp = [[[-1, -float("inf")] for _ in range(2)] for _ in range(K + 1)]
dp[0][0][0] = 0
dp[0][0][1] = 0


def update(top2: list[list[int]], color: int, value: int):
    c0, v0 = top2[0]
    c1, v1 = top2[1]

    if color == c0:
        # 色が同じなら、最大値を更新する
        top2[0][1] = max(v0, value)
    elif color == c1:
        # 色が同じなら、最大値を更新する
        top2[1][1] = max(v1, value)
        # 2 番目の最大値が最大値を超える可能性があるので、確認して必要ならスワップ
        if top2[1][1] > top2[0][1]:
            top2[:] = top2[::-1]
    else:
        if value > v0:
            top2[1][:] = top2[0][:]
            top2[0][:] = color, value
        elif value > v1:
            top2[1][:] = color, value

    return


for _ in range(N):
    c, v = map(int, input().split())

    for k in range(K, -1, -1):
        c0, v0 = dp[k][0]
        c1, v1 = dp[k][1]

        # i 番目のボールをとる
        update(dp[k], c, (v0 if c0 != c else v1) + v)

        # i 番目のボールを取らない
        if k:
            update(dp[k], dp[k - 1][0][0], dp[k - 1][0][1])
            update(dp[k], dp[k - 1][1][0], dp[k - 1][1][1])


if dp[K][0][1] < 0:
    print(-1)
else:
    print(dp[K][0][1])
