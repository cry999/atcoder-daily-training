from collections import defaultdict

S = input()

hist = defaultdict(list)

for i, c in enumerate(S):
    hist[c].append(i)

ans = 0
for indexes in hist.values():
    s = indexes[0] + 1
    i = 1
    for k in indexes[1:]:
        ans += i * k - s
        s += k + 1
        i += 1
print(ans)
