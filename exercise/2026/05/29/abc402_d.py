from collections import Counter

N, M = map(int, input().split())
count = Counter([sum(map(int, input().split())) % N for _ in range(M)])
print(M * (M - 1) // 2 - sum(c * (c - 1) // 2 for c in count.values()))
