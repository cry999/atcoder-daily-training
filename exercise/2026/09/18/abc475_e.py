# >>> atcoder-stat >>>
# started_at  = 2026-09-18T10:58:04+09:00
# solved_at   = 2026-09-18T11:06:43+09:00
# duration_ms = 519035
# ac          = true
# editorial   = false
# knowledge   = 3
# translation = 3
# complexity  = 3
# impl        = 3
# verify      = 3
# <<< atcoder-stat <<<
from sortedcontainers import SortedList
import sys

input = sys.stdin.readline


N, M, K = map(int, input().split())
T = input()
S = [
    "".join("0" if s == t else "1" for s, t in zip(input().strip(), T))
    for _ in range(N)
]

ordered = SortedList(S)

Q = int(input())
for _ in range(Q):
    i, j = map(int, input().split())
    i, j = i - 1, j - 1

    s = S[i]
    print(f"[DEBUG] before {s=}: {ordered=}")
    ordered.remove(s)
    s = s[:j] + ("1" if s[j] == "0" else "0") + s[j + 1 :]
    ordered.add(s)
    print(f"[DEBUG] after {s=}: {ordered=}")
    S[i] = s

    rank = ordered.bisect_right(s)
    if any(s[i] != "1" for i in range(K)) and rank <= M:
        print("Yes")
    else:
        print("No")
