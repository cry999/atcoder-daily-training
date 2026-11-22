# >>> atcoder-stat >>>
# started_at  = 2026-11-19T17:44:27+09:00
# solved_at   = 2026-11-19T17:48:36+09:00
# duration_ms = 249316
# ac          = true
# editorial   = false
# knowledge   = 3
# translation = 3
# complexity  = 3
# impl        = 3
# verify      = 3
# <<< atcoder-stat <<<
from collections import deque

N, Q = map(int, input().split())
(*K,) = map(int, input().split())

q: deque[int] = deque()
deck = list(range(N, 0, -1))
for k in K:
    for _ in range(k):
        q.append(deck.pop())
    while q:
        deck.append(-q.popleft())

for c in deck[::-1]:
    print(c)
