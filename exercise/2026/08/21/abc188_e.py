# >>> atcoder-stat >>>
# started_at  = 2026-08-21T23:39:01+09:00
# solved_at   = 2026-08-21T23:46:09+09:00
# duration_ms = 428937
# ac          = true
# editorial   = false
# knowledge   = 3
# translation = 3
# complexity  = 3
# impl        = 3
# verify      = 3
# <<< atcoder-stat <<<
N, M = map(int, input().split())
(*A,) = map(int, input().split())

g = [[] for _ in range(N)]
for _ in range(M):
    x, y = map(int, input().split())
    x, y = x - 1, y - 1
    g[x].append(y)

INF = 10**18

# min_price[i] := i に到達するまでに買うことができる商品の最小の値段
min_price = [INF] * N

ans = -INF
for i in range(N):
    ans = max(ans, A[i] - min_price[i])

    for j in g[i]:
        min_price[j] = min(min_price[j], A[i], min_price[i])

print(ans)
