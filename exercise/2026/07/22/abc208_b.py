# >>> atcoder-stat >>>
# started_at  = 2026-07-22T15:50:50+09:00
# solved_at   = 2026-07-22T16:00:53+09:00
# duration_ms = 603102
# ac          = true
# editorial   = false
# knowledge   = 3
# translation = 3
# complexity  = 3
# impl        = 3
# verify      = 3
# <<< atcoder-stat <<<
P = int(input())
# 桁 DP?
M = 10
coin = 3_628_800
ans = 0
for m in range(M, 0, -1):
    print(f"[DEBUG] {m=} {coin=}")
    q, r = divmod(P, coin)
    ans += q
    P = r
    coin //= m
print(ans)
