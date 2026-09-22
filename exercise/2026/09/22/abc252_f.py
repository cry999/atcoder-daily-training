# >>> atcoder-stat >>>
# started_at  = 2026-09-22T02:41:33+09:00
# solved_at   = 2026-09-22T02:45:21+09:00
# duration_ms = 228576
# ac          = true
# editorial   = false
# knowledge   = 3
# translation = 3
# complexity  = 3
# impl        = 3
# verify      = 3
# <<< atcoder-stat <<<
import heapq

N, L = map(int, input().split())
(*A,) = map(int, input().split())

# 重要な考察
# 1. A[i] を切り出すのが遅れるほど、コストに対する寄与は大きくなる
# 2. 1 により、大きい A[i] はなるべく最初に処理した方が良い。
# 3. 操作を逆に考える。切り出された A[i] (+L-sum(A)) を繋げて L のパンを作ることを考える
# 4. 2 により、小さい順に繋げていけば良い。

rest = L - sum(A)
if rest:
    A.append(rest)

heapq.heapify(A)
ans = 0
while len(A) > 1:
    merged = heapq.heappop(A) + heapq.heappop(A)
    ans += merged
    heapq.heappush(A, merged)
print(ans)
