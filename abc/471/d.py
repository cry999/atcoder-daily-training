from sortedcontainers import SortedList

Q, V = map(int, input().split())

batteries = SortedList()

for _ in range(Q):
    q, *args = map(int, input().split())
    # print(f"[DEBUG] {q=} {args=}")
    # print(f"[DEBUG] {batteries=}")
    if q == 1:
        t, w = args
        batteries.add((w - t, t, w))
    else:
        t = args[0]
        if batteries:
            _, t0, w0 = batteries.pop()
            v = min(V, w0 + t - t0)
        else:
            v = -1
        print(v)
