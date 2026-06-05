L, R = map(int, input().split())

ans = []
l = L
r = l + 1
while True:
    pow2 = 1
    while l % pow2 == 0 and r < R:
        n = (l // pow2 + 1) * pow2
        if n > R:
            break
        r = max(r, n)
        pow2 *= 2

    ans.append((l, r))
    if r == R:
        break
    l, r = r, r + 1

print(len(ans))
for l, r in ans:
    print(l, r)
