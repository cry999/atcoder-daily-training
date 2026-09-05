# >>> atcoder-stat >>>
# started_at  = 2026-09-05T10:31:07+09:00
# solved_at   = 2026-09-05T10:35:36+09:00
# duration_ms = 269498
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

note = {}
tree = [(-1, 0)]  # (値, 親)
cur = 0
ans = []
for _ in range(Q):
    query, *args = input().split()
    if query == "ADD":
        x = int(args[0])
        new = (x, cur)
        cur = len(tree)
        tree.append(new)
    elif query == "DELETE":
        _, cur = tree[cur]
    elif query == "SAVE":
        y = int(args[0])
        note[y] = cur
    else:  # LOAD
        z = int(args[0])
        cur = note.get(z, 0)

    ans.append(tree[cur][0])

print(*ans)
