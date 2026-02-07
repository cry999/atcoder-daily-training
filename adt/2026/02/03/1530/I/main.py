N, M = map(int, input().split())

verticals = set()
horizontals = set()
plus_diagonals = set()
minus_diagonals = set()

for _ in range(M):
    a, b = map(int, input().split())

    verticals.add(b)
    horizontals.add(a)
    plus_diagonals.add(a + b)
    minus_diagonals.add(a - b)

# 縦・横を除外しておく。
total = (N - len(verticals)) * (N - len(horizontals))
# print(f"{total=}")

# / を計算する
for d in plus_diagonals:
    duplicated = set()
    for v in verticals:
        if 0 < d - v <= N:
            duplicated.add((d - v, v))
    for h in horizontals:
        if 0 < d - h <= N:
            duplicated.add((h, d - h))

    # print(f"{d=}, diff={N - abs(N+1-d)-len(duplicated)}, {duplicated=}")
    total -= N - abs(N + 1 - d) - len(duplicated)

# print(f"{total=}")
# \ を計算する
for d in minus_diagonals:
    duplicated = set()

    for v in verticals:
        if 0 < v + d <= N:
            duplicated.add((v + d, v))
    for h in horizontals:
        if 0 < h - d <= N:
            duplicated.add((h, h - d))
    for p in plus_diagonals:
        if (p + d) % 2:
            continue
        if not 0 < (p + d) // 2 <= N:
            continue
        if not 0 < (p - d) // 2 <= N:
            continue
        node = ((p + d) // 2, (p - d) // 2)
        duplicated.add(node)

    # print(f"{d=}, diff={N - abs(d) - len(duplicated)}, {duplicated=}")
    total -= N - abs(d) - len(duplicated)


print(total)
