# >>> atcoder-stat >>>
# started_at  = 2026-09-18T11:23:03+09:00
# solved_at   = 2026-09-18T11:27:47+09:00
# duration_ms = 284676
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
# 1. 合計コストへの各 A[i] の寄与は、後回しにされるほど回数が多くなる
# 2. したがって、A[i] の値が大きいものをさっさと削除したい。
# 3. 逆に考えて、A[i] の値が小さいもの、あるいはいくつか選んだうちの合計が残りのパンよりも小さいものから
# 順にくっつけていって L のパンを復元すると良い。

r = L - sum(A)
if r > 0:
    A.append(r)

ans = 0
heapq.heapify(A)
while len(A) > 1:
    merged = heapq.heappop(A) + heapq.heappop(A)
    ans += merged
    heapq.heappush(A, merged)
print(ans)
