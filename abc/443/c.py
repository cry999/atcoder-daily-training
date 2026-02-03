N, T = map(int, input().split())
(*A,) = map(int, input().split())

now = 0

ans = 0
for a in A:
    if a <= now:
        continue

    ans += a - now
    now = a + 100
if now < T:
    ans += T - now
print(ans)
