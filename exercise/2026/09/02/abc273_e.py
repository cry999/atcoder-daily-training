# >>> atcoder-stat >>>
# started_at  = 2026-09-02T16:12:58+09:00
# solved_at   = 2026-09-02T16:30:30+09:00
# duration_ms = 1052424
# ac          = true
# editorial   = true
# knowledge   = 2
# translation = 1
# complexity  = 3
# impl        = 2
# verify      = 3
# <<< atcoder-stat <<<
import sys

input = sys.stdin.readline


Q = int(input())
# note[page] = node: page に書かれている数列の末尾の木上での頂点を保持
note = {}
tree = [(-1, -1)]  # (値, 親)
cur = 0
ans = []
for _ in range(Q):
    q, *args = input().split()

    if q == "ADD":
        x = int(args[0])
        new_node = (x, cur)
        cur = len(tree)
        tree.append(new_node)
    elif q == "DELETE":
        if cur != 0:
            # 親に移動
            cur = tree[cur][1]
    elif q == "SAVE":
        p = int(args[0])
        note[p] = cur
    else:  # q == 'LOAD'
        p = int(args[0])
        cur = note.get(p, 0)

    ans.append(tree[cur][0])

print(*ans)
