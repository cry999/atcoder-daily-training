H, W = map(int, input().split())
c = [input() for _ in range(H)]


def C(i: int, j: int) -> str:
    if 0 <= i < H and 0 <= j < W:
        return c[i][j]
    return "."


ans = [0] * (min(H, W) + 1)
for a in range(H):
    for b in range(W):
        if C(a, b) == ".":
            continue

        for n in range(1, min(H, W)):
            if all(
                C(a + di, b + dj) == "#"
                for di, dj in [(n, n), (-n, n), (n, -n), (-n, -n)]
            ):
                continue
            ans[n - 1] += 1
            break
print(*ans[1:])
