from sortedcontainers import SortedDict

N = int(input())
d = SortedDict()

for _ in range(N):
    s, c = map(int, input().split())
    d[s] = d.get(s, 0) + c

ans = 0

while d:
    s, c = d.popitem(0)

    if c >= 2:
        d[2 * s] = d.get(2 * s, 0) + c // 2
    ans += c % 2

print(ans)
