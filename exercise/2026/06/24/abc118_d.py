N, M = map(int, input().split())
(*A,) = map(int, input().split())

X = {
    1: 2,
    2: 5,
    3: 5,
    4: 4,
    5: 5,
    6: 6,
    7: 3,
    8: 7,
    9: 6,
}


def cmp(a: tuple[int], b: tuple[int]):
    sa = sum(a)
    sb = sum(b)

    if sa == sb:
        for i in range(9, 0, -1):
            if a[i - 1] == b[i - 1]:
                continue
            return 1 if a[i - 1] > b[i - 1] else -1
        return 0

    return 1 if sa > sb else -1


def max(a: tuple[int], b: tuple[int]):
    if cmp(a, b) >= 0:
        return a
    return b


def display(v: tuple[int]):
    return "".join(str(i) * v[i - 1] for i in range(9, 0, -1))


ZERO = tuple(0 for _ in range(9))

memo = {}
for a in A:
    x = X[a]
    memo[x] = max(
        memo.get(x, ZERO),
        tuple(int(i + 1 == a) for i in range(9)),
    )

for n in range(N + 1):
    for a in A:
        x = X[a]
        if n - x not in memo:
            continue
        # print(f"[DEBUG] update {n=} with {x=}")
        v = memo[n - x]
        new_v = tuple(v[i] + 1 if i + 1 == a else v[i] for i in range(9))
        memo[n] = max(memo.get(n, ZERO), new_v)

print(display(memo[N]))
