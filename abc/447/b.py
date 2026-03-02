S = input()
hist = {}

for c in S:
    hist[c] = hist.get(c, 0) + 1

max_hist = max(hist.values())

ans = []
for c in S:
    if hist[c] == max_hist:
        continue
    ans.append(c)

print("".join(ans))
