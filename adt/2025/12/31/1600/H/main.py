N = int(input())
(*A,) = map(int, input().split())

lo, hi = 0, max(A) * (10**3) + 1
while hi - lo > 1:
    mi = (lo + hi) // 2
    dp = [[0] * 2 for _ in range(N + 1)]

    for i in range(N):
        dp[i + 1][0] = dp[i][1]
        dp[i + 1][1] = max(dp[i][0], dp[i][1]) + A[i] * (10**3) - mi

    if max(dp[N]) >= 0:
        lo = mi
    else:
        hi = mi
print(f"{lo/1000:.4f}")

sorted_a = sorted(A)
lo, hi = 0, N
while hi - lo > 1:
    mi = (lo + hi) // 2
    dp = [[0] * 2 for _ in range(N + 1)]

    for i in range(N):
        dp[i + 1][0] = dp[i][1]
        dp[i + 1][1] = max(dp[i][0], dp[i][1]) + (1 if A[i] >= sorted_a[mi] else -1)

    if max(dp[N]) > 0:
        lo = mi
    else:
        hi = mi

print(f"{sorted_a[lo]}")
