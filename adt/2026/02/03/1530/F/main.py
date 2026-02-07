from sortedcontainers import SortedSet

N, K = map(int, input().split())
A = SortedSet(map(int, input().split()))

c = 0
for i in range(min(len(A), K)):
    a = A[i]
    if c == a:
        c += 1
    else:
        break

print(c)
