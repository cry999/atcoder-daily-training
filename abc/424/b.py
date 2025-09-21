N, M, K = map(int, input().split())

dp = [0] * N
all_right = (1 << M) - 1
perfects = []

for i in range(K):
    A, B = map(int, input().split())
    dp[A-1] |= 1 << (B-1)
    if dp[A-1] == all_right:
        perfects.append(A)

if perfects:
    print(*perfects)
