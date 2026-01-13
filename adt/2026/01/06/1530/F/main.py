(*S,) = map(int, list(input()))

compressed = [(S[0], 0)]

for s in S:
    p, cnt = compressed[-1]
    if p == s:
        compressed[-1] = (p, cnt + 1)
    else:
        compressed.append((s, 1))

ans = 0
for i in range(len(compressed) - 1):
    s0, c0 = compressed[i]
    s1, c1 = compressed[i + 1]

    if s0 + 1 != s1:
        continue

    ans += min(c0, c1)

print(ans)
