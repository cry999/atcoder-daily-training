from collections import defaultdict


N = int(input())
*A, = map(int, input().split())

hist = defaultdict(int)
f = []
for i, a in enumerate(A):
    hist[a] += 1
    if hist[a] == 2:
        f.append((i, a))

f.sort()
print(*map(lambda x: x[1], f))
