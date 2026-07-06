L = int(input())
N = int(input())
M = int(input())
D = [0] + [int(input()) for _ in range(N - 1)] + [L]
D.sort()

ans = 0
for _ in range(M):
    k = int(input())
    lo, hi = 0, N + 1
    while hi > lo:
        mid = (hi + lo) // 2
        if D[mid] <= k:
            lo = mid + 1
        else:
            hi = mid

    if D[lo] == k:
        ans += 0
    else:
        ans += min(k - D[lo - 1], D[lo] - k)
print(ans)
