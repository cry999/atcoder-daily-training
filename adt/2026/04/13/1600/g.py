N = int(input())
D = [list(map(int, input().split())) for _ in range(N - 1)]

memo = {}


def solve(used: set[int]) -> int:
    c = 0
    for u in used:
        c |= 1 << u
    if c in memo:
        return memo[c]

    if len(used) + 2 == N:
        x, y = [i for i in range(N) if i not in used]
        return D[x][y - x - 1]
    if len(used) + 3 == N:
        x, y, z = sorted(i for i in range(N) if i not in used)
        return max(D[x][y - x - 1], D[x][z - x - 1], D[y][z - y - 1])

    for x in range(N):
        for y in range(x + 1, N):
            if x == y or x in used or y in used:
                continue
            memo[c] = max(memo.get(c, 0), solve(used | {x, y}) + D[x][y - x - 1])

    return memo[c]


print(solve(set()))
