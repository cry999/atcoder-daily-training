T = int(input())

for _ in range(T):
    N = int(input())
    (*A,) = map(int, input().split())

    candidates = [[(-1, -1), (-1, -1)] * 2 for _ in range(N + 1)]
    can_use = [True] * (N + 1)

    ans = set()
    for i in range(2 * N):
        a = A[i]
        b1 = A[i - 1] if i - 1 >= 0 else -1
        b2 = A[i + 1] if i + 1 < 2 * N else -1
        if a == b1 or a == b2:
            can_use[a] = False
            continue
        if b1 == b2:
            b2 = -1

        # print(f"=== i: {i}, {a=}, {b1=}, {b2=}")
        c1, i1 = candidates[a][0]
        c2, i2 = candidates[a][1]
        if c1 == c2 == -1:
            candidates[a][0] = (b1, i - 1)
            candidates[a][1] = (b2, i + 1)
        else:
            if (
                (b1 == c1 and i - 1 != i1 or b1 == c2 and i - 1 != i2)
                and b1 != -1
                and can_use[b1]
            ):
                # print(f"  {b1=}, {c1=}, {c2=}")
                # ans += a < b1
                ans.add((min(a, b1), max(a, b1)))
            if (
                (b2 == c1 and i + 1 != i1 or b2 == c2 and i + 1 != i2)
                and b2 != -1
                and can_use[b2]
            ):
                # print(f"  {b2=}, {c1=}, {c2=}")
                # ans += a < b2
                ans.add((min(a, b2), max(a, b2)))
    print(len(ans))
