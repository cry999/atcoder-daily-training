import bisect
# とりあえず brute force で解く
# N <= 10^4, Q=5x10^5 で O(NQ) なので 5x10^9 回のループになり TLE

N = int(input())
PAB = list(tuple(map(int, input().split())) for _ in range(N))

MAX_PA = 1001
# dp[i][j] := i 番目のプレゼントを受け取った直後のテンションが値 j の時の、
# 最終的なテンションの値
dp = [[0] * (MAX_PA + 1) for _ in range(N+1)]

for j in range(MAX_PA + 1):
    dp[N][j] = j

for i in range(N-1, -1, -1):
    P, A, B = PAB[i]
    for j in range(MAX_PA + 1):
        if j <= P:
            dp[i][j] = dp[i+1][j+A]
        else:
            dp[i][j] = dp[i+1][max(0, j-B)]

sum_b = [0] * (N+1)
for i in range(N):
    sum_b[i+1] = sum_b[i] + PAB[i][2]

Q = int(input())
for _ in range(Q):
    X = int(input())

    i = bisect.bisect_left(sum_b, X-MAX_PA)
    if i == N+1:
        print(X-sum_b[N])
    else:
        print(dp[i][X-sum_b[i]])
