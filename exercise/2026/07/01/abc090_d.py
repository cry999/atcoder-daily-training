# >>> atcoder-stat >>>
# started_at  = 2026-07-01T18:38:34+09:00
# solved_at   = 2026-07-01T19:15:15+09:00
# duration_ms = 2201758
# target_ms   = 900000
# ac          = true
# editorial   = false
# knowledge   = 3
# translation = 2
# complexity  = 3
# impl        = 2
# verify      = 3
# <<< atcoder-stat <<<

N, K = map(int, input().split())
if K == 0:
    print(N * N)
    exit()

ans = 0
for b in range(K + 1, N + 1):
    # bq + K <= a <= max(bq + b - 1, N) を満たす a が存在する q を数える
    # その q に対して、a は bq + K, ..., bq + b-1 の b-K 個存在する。
    # 最後の q については、N < bq+b-1 の可能性がある。
    q_max = (N - K) // b

    print(f"[DEBUG] {b=} {q_max=}")
    ans += q_max * (b - K)

    if b * q_max + b - 1 <= N:
        ans += b - K
    else:
        ans += N % b - K + 1
print(ans)
