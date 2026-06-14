N = int(input())
A = [list(map(int, input().split())) for _ in range(2 * N - 1)]


def combinations(bit: int):
    if bit + 1 == 1 << (2 * N):
        yield []
        return

    for i in range(2 * N):
        if bit & (1 << i):
            continue

        for j in range(i + 1, 2 * N):
            if bit & (1 << j):
                continue

            nxt = bit | (1 << i) | (1 << j)

            for comb in combinations(nxt):
                res = [(i, j)]
                res.extend(comb)
                yield res

        return


ans = 0
for comb in combinations(0):
    score = 0
    for i, j in comb:
        score ^= A[i][j - i - 1]
    ans = max(ans, score)
print(ans)
