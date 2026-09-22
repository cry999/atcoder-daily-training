# >>> atcoder-stat >>>
# started_at  = 2026-09-21T10:34:11+09:00
# solved_at   = 2026-09-21T10:38:58+09:00
# duration_ms = 287510
# ac          = true
# editorial   = false
# knowledge   = 3
# translation = 3
# complexity  = 3
# impl        = 3
# verify      = 3
# <<< atcoder-stat <<<
import sys

input = sys.stdin.readline


# history := (parent, value)
history = [(0, -1)]

Q = int(input())
cursor = 0
note = {}
ans = []
for _ in range(Q):
    q, *args = input().split()

    if q == "ADD":
        x = int(args[0])
        node = (cursor, x)
        cursor = len(history)
        history.append(node)
    elif q == "DELETE":
        cursor = history[cursor][0]
    elif q == "SAVE":
        y = int(args[0])
        note[y] = cursor
    else:  # LOAD
        z = int(args[0])
        cursor = note.get(z, 0)

    ans.append(history[cursor][1])
print(*ans)
