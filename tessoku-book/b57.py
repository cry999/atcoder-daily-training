N, K = map(int, input().split())


def operate(i: int) -> int:
    d = i
    s = 0
    while d:
        if d % 10:
            s += d % 10
        d //= 10
    return i-s


dp = [[0] * (N+1) for _ in range(32)]
for i in range(1, N+1):
    dp[0][i] = operate(i)

for k in range(31):
    for n in range(N+1):
        dp[k+1][n] = dp[k][dp[k][n]]

# print(dp)
for n in range(1, N+1):
    k, j = K, 0
    while k:
        if k & (1 << j) == 0:
            j += 1
            continue
        n = dp[j][n]
        k -= (1 << j)
        j += 1
    print(n)
