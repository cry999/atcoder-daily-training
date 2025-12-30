from collections import defaultdict


beans = defaultdict(lambda : float('inf'))
N = int(input())

for _ in range(N):
    a, c = map(int, input().split())
    beans[c] = min(beans[c], a)

print(max(beans.values()))
