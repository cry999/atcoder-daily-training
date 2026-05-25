N = int(input())
(*A,) = map(int, input().split())

ans = 0

hist = {}
for a in A:
    if a % 5 == 0:
        ans += hist.get(a // 5 * 3, 0) * hist.get(a // 5 * 7, 0)

    hist[a] = hist.get(a, 0) + 1

hist = {}
for a in A[::-1]:
    if a % 5 == 0:
        ans += hist.get(a // 5 * 3, 0) * hist.get(a // 5 * 7, 0)

    hist[a] = hist.get(a, 0) + 1

print(ans)
