from collections import defaultdict

S = input()

indexes = defaultdict(list)
for i, c in enumerate(S):
    indexes[c].append(i)

ans = 0
for v in indexes.values():
    if len(v) <= 1:
        continue

    n = len(v)
    for i in range(n):
        ans += v[n - 1 - i] * (n - (2 * i + 1))
    ans -= n * (n - 1) // 2
print(ans)
