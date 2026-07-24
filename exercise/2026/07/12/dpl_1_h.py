N, W = map(int, input().split())


def knapsack(W: int, v: list[int], w: list[int]):
    """全列挙して、重さに対して価値が単調増加するように並べて返す。"""
    states = [(0, 0)]

    for wi, vi in zip(w, v):
        new_states = []
        for wj, vj in states:
            if wi + wj <= W:
                new_states.append((wi + wj, vi + vj))
        states.extend(new_states)

    states.sort()

    res = []
    for ww, vv in states:
        if res and res[-1][0] == ww:
            res.pop()
        if res and res[-1][1] >= vv:
            continue
        res.append((ww, vv))

    return res


v = [0] * (N // 2)
w = [0] * (N // 2)
for i in range(N // 2):
    v[i], w[i] = map(int, input().split())
s1 = knapsack(W, v, w)

M = N - N // 2
v = [0] * M
w = [0] * M
for i in range(M):
    v[i], w[i] = map(int, input().split())
s2 = knapsack(W, v, w)

ans = 0

i2 = len(s2) - 1
for w1, v1 in s1:
    w2, v2 = s2[i2]
    while i2 > 0 and w1 + w2 > W:
        i2 -= 1
        w2, v2 = s2[i2]
    # print(f"[DEBUG] {i1=} {i2=}: {v1+v2=} @ {w1+w2=}")
    ans = max(ans, v1 + v2)
print(ans)
