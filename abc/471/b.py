from collections import Counter

N = int(input())

c = Counter([input().lower() for _ in range(N)])
print(max(c.values()))
