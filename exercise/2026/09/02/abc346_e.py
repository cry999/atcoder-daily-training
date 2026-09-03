# >>> atcoder-stat >>>
# started_at  = 2026-09-02T15:49:21+09:00
# solved_at   = 2026-09-02T16:12:13+09:00
# duration_ms = 1372541
# ac          = true
# editorial   = false
# knowledge   = 3
# translation = 2
# complexity  = 3
# impl        = 2
# verify      = 3
# <<< atcoder-stat <<<
import sys
from collections import defaultdict

input = sys.stdin.readline


H, W, M = map(int, input().split())

queries = []
for _ in range(M):
    t, a, x = map(int, input().split())
    a -= 1

    queries.append((t, a, x))
queries.reverse()


counter = defaultdict(int)
counter[0] = H * W
used_row = [False] * H
used_col = [False] * W
rem_row, rem_col = H, W
for t, a, x in queries:
    if t == 1:
        # 行 a を x にする
        if used_row[a]:
            # 上塗りされているので無視
            continue
        used_row[a] = True
        counter[0] -= rem_col
        counter[x] += rem_col
        rem_row -= 1
    else:  # t == 2
        # 列 a を x にする
        if used_col[a]:
            # 上塗りされているので無視
            continue
        used_col[a] = True
        counter[0] -= rem_row
        counter[x] += rem_row
        rem_col -= 1

ans = []
for k in sorted(counter):
    if counter[k] == 0:
        continue
    ans.append(k)

print(len(ans))
for k in ans:
    print(k, counter[k])
