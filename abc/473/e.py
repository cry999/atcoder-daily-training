N, K = map(int, input().split())
(*A,) = map(int, input().split())

ans = 0
s = 0

r = {}
r[0] = 0
for a in A:
    s += a
    s %= K

    if s in r:
        ans = max(ans, r[s] + 1)
        r[s] = max(r[s], ans)
    else:
        r[s] = ans

print(ans)
