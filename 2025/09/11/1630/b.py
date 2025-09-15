N, M = map(int, input().split())
H = list(map(int, input().split()))

C = [0] * (N+1)
for i in range(N):
    C[i+1] = C[i] + H[i]

lo, hi = 0, N
while lo <= hi:
    mid = (lo + hi) // 2
    if C[mid] > M:
        hi = mid - 1
    elif C[mid] < M:
        lo = mid + 1
    else:
        lo = hi = mid
        break

print(min(lo, hi))
