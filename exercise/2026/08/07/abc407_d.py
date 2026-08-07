# >>> atcoder-stat >>>
# started_at  = 2026-08-07T14:43:09+09:00
# solved_at   = 2026-08-07T14:56:42+09:00
# duration_ms = 813568
# target_ms   = 900000
# ac          = true
# editorial   = false
# knowledge   = 3
# translation = 3
# complexity  = 3
# impl        = 3
# verify      = 3
# <<< atcoder-stat <<<
import sys

sys.setrecursionlimit(10**7)

H, W = map(int, input().split())
A = [list(map(int, input().split())) for _ in range(H)]

X = 0
for p in range(H * W):
    h, w = divmod(p, W)
    X ^= A[h][w]


def all_state(s: int, p: int):
    if p == H * W:
        yield s
        return

    h, w = divmod(p, W)
    # (h, w) と (h, w+1) にドミノをおく
    if w + 1 < W and s & (1 << p) == s & (1 << (p + 1)) == 0:
        yield from all_state(s | (1 << p) | (1 << (p + 1)), p + 1)

    # (h, w) と (h+1, w) にドミノをおく
    if h + 1 < H and s & (1 << p) == s & (1 << (p + W)) == 0:
        yield from all_state(s | (1 << p) | (1 << (p + W)), p + 1)

    # (h, w) にドミノを置かない
    yield from all_state(s, p + 1)

    return


ans = 0
for s in all_state(0, 0):
    x = X
    for p in range(H * W):
        h, w = divmod(p, W)
        if s & (1 << p):
            x ^= A[h][w]
    ans = max(ans, x)
print(ans)
