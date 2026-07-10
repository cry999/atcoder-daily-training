MOD = 10**5
N, M = map(int, input().split())
dist = [int(input()) for _ in range(N - 1)]
diff = [int(input()) for _ in range(M)]

# cum[i] := 0 から i までの移動距離
cum = [0] * N
for i in range(1, N):
    cum[i] = cum[i - 1] + dist[i - 1]

cur = 0
ans = 0
for d in diff:
    nxt = cur + d
    ans += cum[max(cur, nxt)] - cum[min(cur, nxt)]
    ans %= MOD
    cur = nxt
print(ans)
