# >>> atcoder-stat >>>
# started_at  = 2026-09-03T14:24:46+09:00
# solved_at   = 2026-09-03T14:30:31+09:00
# duration_ms = 345424
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


Q = int(input())
tree = [(-1, 0)]
note = {}
cur = 0
ans = []
for _ in range(Q):
    query, *args = input().split()
    if query == "ADD":
        x = int(args[0])
        nxt = (x, cur)
        cur = len(tree)
        tree.append(nxt)
    elif query == "DELETE":
        cur = tree[cur][1]
    elif query == "SAVE":
        y = int(args[0])
        note[y] = cur
    else:  # LOAD
        z = int(args[0])
        cur = note.get(z, 0)

    ans.append(tree[cur][0])

print(*ans)
