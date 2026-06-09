from bisect import bisect_left
from collections import defaultdict

H, W, rs, cs = map(int, input().split())
N = int(input())
wall_r = defaultdict(list)
wall_c = defaultdict(list)
for _ in range(N):
    r, c = map(int, input().split())
    wall_r[r].append(c)
    wall_c[c].append(r)

for i in wall_r.keys():
    wall_r[i].append(0)
    wall_r[i].append(W + 1)
    wall_r[i].sort()

for j in wall_c.keys():
    wall_c[j].append(0)
    wall_c[j].append(H + 1)
    wall_c[j].sort()

Q = int(input())
default_wall_r = [0, W + 1]
default_wall_c = [0, H + 1]
for _ in range(Q):
    d, raw_l = input().split()
    l = int(raw_l)

    if d == "L":
        w = wall_r.get(rs, default_wall_r)
        i = bisect_left(w, cs)
        cw = w[i - 1]
        cs -= min(l, cs - cw - 1)
    elif d == "R":
        w = wall_r.get(rs, default_wall_r)
        i = bisect_left(w, cs)
        cw = w[i]
        cs += min(l, cw - cs - 1)
    elif d == "U":
        w = wall_c.get(cs, default_wall_c)
        i = bisect_left(w, rs)
        rw = w[i - 1]
        rs -= min(l, rs - rw - 1)
    else:
        w = wall_c.get(cs, default_wall_c)
        i = bisect_left(w, rs)
        rw = w[i]
        rs += min(l, rw - rs - 1)

    print(rs, cs)
