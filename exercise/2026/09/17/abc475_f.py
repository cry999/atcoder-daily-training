# >>> atcoder-stat >>>
# started_at  = 2026-09-17T11:11:46+09:00
# solved_at   = 2026-09-17T16:16:30+09:00
# duration_ms = 18284182
# ac          = true
# editorial   = false
# knowledge   = 2
# translation = 2
# complexity  = 2
# impl        = 1
# verify      = 2
# <<< atcoder-stat <<<
import sys

input = sys.stdin.readline


H, W = map(int, input().split())

if H > W:
    whites = [[False] * H for _ in range(W)]
    for h in range(H):
        for w, s in enumerate(input().strip()):
            whites[w][h] = s == "."
    H, W = W, H
else:
    whites = [[s == "." for s in input().strip()] for _ in range(H)]


ans = 1

prefix = [0] * (W + 1)
has_white = [False] * W
for top in range(H):
    for w in range(W):
        has_white[w] = whites[top][w]

    for bottom in range(top, H):
        last_top, last_bottom = -1, -1
        prefix[0] = 0

        for w in range(W):
            has_white[w] |= whites[bottom][w]

        for right in range(W):
            if whites[top][right]:
                last_top = right

            if whites[bottom][right]:
                last_bottom = right

            prefix[right + 1] = prefix[right] + has_white[right]
            if not has_white[right]:
                continue

            limit = min(last_top, last_bottom)
            ans += prefix[limit + 1]

print(ans)
