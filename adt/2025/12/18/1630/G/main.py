from collections import defaultdict


N = int(input())
*A, = map(int, input().split())

ans = 0
for i in range(2):
    j = i
    hist = defaultdict(int)
    while i+1 < N and j+1 < N:
        if i+1 < N and A[i] != A[i+1]:
            i += 2
            continue

        j = max(j, i)
        while j+1 < N and A[j] == A[j+1] and not hist[A[j]]:
            hist[A[j]] += 1
            j += 2

        ans = max(ans, j-i)
        if i == j:
            i += 2
            continue
        hist[A[i]] -= 1
        i += 2

print(ans)
