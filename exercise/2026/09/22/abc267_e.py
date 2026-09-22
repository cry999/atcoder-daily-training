# >>> atcoder-stat >>>
# started_at  = 2026-09-22T01:59:11+09:00
# solved_at   = 2026-09-22T02:07:23+09:00
# duration_ms = 492723
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


N, M = map(int, input().split())
(*A,) = map(int, input().split())

g = [[] for _ in range(N)]
for _ in range(M):
    u, v = map(int, input().split())
    u, v = u - 1, v - 1
    g[u].append(v)
    g[v].append(u)

init_score = [sum(A[v] for v in g[u]) for u in range(N)]

# 重要な考察
# 1. コスト X で操作が完了するなら X 以上で完了できる -> 単調性
# 2. X を固定した時、一度コスト X で削除可能になったノードはその後どんな操作が行われても削除可能

score = init_score[:]
lo, hi = -1, max(score) + 1
while hi - lo > 1:
    x = (lo + hi) // 2

    score[:] = init_score[:]
    q = [u for u in range(N) if score[u] <= x]
    print(f"[DEBUG] [{x=}] {q=} {score=}")
    removed = set(q)

    for u in q:
        for v in g[u]:
            if v in removed:
                continue
            score[v] -= A[u]
            if score[v] <= x:
                q.append(v)
                removed.add(v)

    if len(removed) == N:
        hi = x
    else:
        lo = x

print(hi)
