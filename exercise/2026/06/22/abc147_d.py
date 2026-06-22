N = int(input())
(*A,) = map(int, input().split())

# dp[j] := A の j ビット目の 1 の個数
dp = [0] * 62
for i in range(N):
    for j in range(62):
        dp[j] += (A[i] >> j) & 1

ans = [0] * 62
for j in range(61):
    for i in range(N):
        a = A[i]

        dp[j] -= (a >> j) & 1
        if (a >> j) & 1:
            ans[j] += (N - i - 1 - dp[j]) % 2
            ans[j + 1] += (N - i - 1 - dp[j]) // 2
        else:
            ans[j] += dp[j] % 2
            ans[j + 1] += dp[j] // 2

        if ans[j] >= 2:
            ans[j + 1] += ans[j] // 2
            ans[j] %= 2

a = 0
for i in range(62):
    a <<= 1
    a += ans[61 - i]
    a %= 10**9 + 7
print(a)
