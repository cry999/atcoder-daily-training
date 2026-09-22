# >>> atcoder-stat >>>
# started_at  = 2026-09-22T16:29:16+09:00
# solved_at   = 2026-09-22T16:35:40+09:00
# duration_ms = 384530
# ac          = true
# editorial   = false
# knowledge   = 3
# translation = 3
# complexity  = 3
# impl        = 3
# verify      = 3
# <<< atcoder-stat <<<
import math

N = int(input())
(*P,) = map(int, input().split())

# 考察
# 1. 変化するのは S_k = sum((0.9)^(k-i) Q[i] for i in range(K)) の部分のみ
# 2. i <= M の中から k 個を選んで S_k を最大化した時、i <= M+1 の中から k+1 個を選んで S_{k+1} 個を最大化するのに S_k は利用できる。
# 3. k を小さい順にやると同じ i を複数回使ってしまう可能性があるので注意

# s[k] := P の中から k 個選んだ時の s_k の最大値
INF = float("inf")
s = [-INF] * (N + 1)
s[0] = 0

for i in range(N):
    for k in range(i, -1, -1):
        s[k + 1] = max(s[k + 1], 0.9 * s[k] + P[i])

ans = -INF
denom = 0
for k in range(1, N + 1):
    denom = 0.9 * denom + 1
    ans = max(ans, s[k] / denom - 1200 / math.sqrt(k))
print(ans)
