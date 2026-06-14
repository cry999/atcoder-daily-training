from collections import Counter

N = int(input())
(*A,) = map(int, input().split())

hist = Counter(A)

keys = sorted(hist.keys())
ans = 0
for q in keys:
    for r in keys:
        if r > keys[-1] // q:
            break
        p = q * r
        if hist[p] == 0:
            continue
        ans += hist[p] * hist[q] * hist[r]
print(ans)
