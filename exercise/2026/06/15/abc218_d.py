N = int(input())

ys = {}
xs = set()

for i in range(N):
    x, y = map(int, input().split())

    ys.setdefault(x, set()).add(y)

(*xs,) = ys.keys()
m = len(xs)

ans = 0
for i in range(m):
    x1 = xs[i]
    if len(ys[x1]) < 2:
        continue

    for j in range(i + 1, m):
        x2 = xs[j]

        d = len(ys[x1] & ys[x2])
        ans += d * (d - 1) // 2
print(ans)
