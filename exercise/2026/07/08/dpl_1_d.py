from bisect import bisect_left

N = int(input())
A = [int(input()) for _ in range(N)]

INF = 10**18
# L[x] := 長さ x の最長増加部分列の最小の右端の数字
L = [INF] * (N + 1)
L[0] = -1

# dp[i] := A[0..i] の最長増加部分列の長さ
dp = [0] * N

for i in range(N):
    x = bisect_left(L, A[i])
    dp[i] = x
    L[x] = min(L[x], A[i])

print(max(dp))
