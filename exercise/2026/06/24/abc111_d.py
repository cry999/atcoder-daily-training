N = int(input())
points = []
parity = 0
for _ in range(N):
    x, y = map(int, input().split())
    parity = (abs(x) + abs(y)) % 2
    points.append((x, y))

if any((abs(x) + abs(y)) % 2 != parity for x, y in points):
    print(-1)
    exit()

arms = [1] * 31
for i in range(30):
    arms[29 - i] = 2 * arms[30 - i]
if parity == 0:
    arms.append(1)

print(len(arms))
print(*arms)

for x, y in points:
    ans = []
    u, v = x + y, x - y
    for d in arms:
        if u >= 0:
            su = 1
            u -= d
        else:
            su = -1
            u += d

        if v >= 0:
            sv = 1
            v -= d
        else:
            sv = -1
            v += d

        if su == sv == 1:
            ans.append("R")
        elif su == sv == -1:
            ans.append("L")
        elif su == 1:
            ans.append("U")
        else:
            ans.append("D")

    assert u == v == 0
    print("".join(ans))
