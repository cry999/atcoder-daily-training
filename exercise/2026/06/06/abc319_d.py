N, M = map(int, input().split())
(*L,) = map(int, input().split())

lo, hi = max(L) - 1, sum(L) + N - 1
while hi - lo > 1:
    mi = (lo + hi) // 2

    # print(f"{lo=}, {hi=}, {mi=}")

    lines = 0
    line_len = 0
    for l in L:
        # print(f"  {l=}, {line_len=}, {lines=}")
        if line_len == 0:
            line_len += l
            lines += 1
        elif line_len + l + 1 <= mi:
            line_len += l + 1
        else:
            line_len = l
            lines += 1

    if lines <= M:
        hi = mi
    else:
        lo = mi

print(hi)
