# >>> atcoder-stat >>>
# started_at  = 2026-07-04T12:37:52+09:00
# solved_at   = 2026-07-04T15:03:40+09:00
# duration_ms = 8748384
# target_ms   = 900000
# ac          = true
# editorial   = false
# knowledge   = 3
# translation = 3
# complexity  = 3
# impl        = 1
# verify      = 3
# <<< atcoder-stat <<<
import sys

input = sys.stdin.readline


H, W, K = map(int, input().split())
S = [input() for _ in range(H)]

C = [[0] * (W + 1) for _ in range(H + 1)]
for p in range(H * W):
    h, w = divmod(p, W)
    if S[h][w] == "1":
        C[h + 1][w + 1] = 1

for h in range(H + 1):
    for w in range(W):
        C[h][w + 1] += C[h][w]
for h in range(H):
    for w in range(W + 1):
        C[h + 1][w] += C[h][w]


def area(h1: int, h2: int, w1: int, w2: int):
    return C[h2][w2] - C[h1][w2] - C[h2][w1] + C[h1][w1]


ans = 0
for h1 in range(H):
    for h2 in range(h1 + 1, H + 1):
        head, tail = 0, 0
        for w1 in range(W):
            head = max(head, w1 + 1)
            while head <= W and area(h1, h2, w1, head) < K:
                head += 1

            tail = max(tail, head)
            while tail <= W and area(h1, h2, w1, tail) == K:
                tail += 1

            ans += tail - head
print(ans)
