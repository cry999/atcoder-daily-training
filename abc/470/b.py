from collections import defaultdict

N = int(input())
(*C,) = map(int, input().split())

counter = defaultdict(int)
for c in C:
    counter[c] += 1

print(N - max(counter.values()))
