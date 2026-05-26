from bisect import bisect_left

N = int(input())
presents = [tuple(map(int, input().split())) for _ in range(N)]

dec = [0] * (N + 1)
for i, (_, _, b) in enumerate(presents):
    dec[i + 1] = dec[i] + b

# dp[i][j] := 気分 j で i 番目以降のプレゼントをもらった時の最終的な気分
dp = [[-1] * (1001) for _ in range(N)]
for x in range(presents[-1][0] + 1):
    dp[-1][x] = x + presents[-1][1]

for x in range(presents[-1][0] + 1, 1001):
    dp[-1][x] = max(x - presents[-1][2], 0)

for i in range(N - 2, -1, -1):
    p, a, b = presents[i]
    for x in range(1001):
        if x <= p:
            dp[i][x] = dp[i + 1][x + a]
        else:
            dp[i][x] = dp[i + 1][max(x - b, 0)]


Q = int(input())
for _ in range(Q):
    X = int(input())

    if X <= 1000:
        print(dp[0][X])
    else:
        i = bisect_left(dec, X - 1000)

        if i < N:
            print(dp[i][X - dec[i]])
        else:
            print(X - dec[-1])
