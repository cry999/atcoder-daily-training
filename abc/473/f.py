from atcoder.segtree import SegTree


def op(x: tuple[int, ...], y: tuple[int, ...]) -> tuple[int]:
    sum_x, min_x = x
    sum_y, min_y = y
    return (sum_x + sum_y, min(min_x, sum_x + min_y))


e = (0, 0)


N = int(input())
S = list(input())

v = []
for c in S:
    if c == "A":
        v.append((1, 0))
    else:
        v.append((-1, -1))

seg = SegTree(op, e, v)

Q = int(input())
for _ in range(Q):
    q, *args = input().split()
    if q == "1":
        i, c = args
        i = int(i) - 1
        if c == S[i]:
            continue
        S[i] = c
        seg.set(i, (1, 0) if c == "A" else (-1, -1))
    else:
        l, r = map(int, args)
        l -= 1
        if seg.prod(l, r)[1] >= 0:
            print("Yes")
        else:
            print("No")
