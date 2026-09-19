N, M = map(int, input().split())
(*A,) = map(int, input().split())
(*B,) = map(int, input().split())

# 考察
# チェビシェフ距離の典型で u = x+y , v = x-y と変換することで一次元で処理できるようにする?

L = 2 * N - 1
ZERO = N - 1

# u, v 方向に変換した後の A[i] * B[j] の寄与分
val_u = [0] * L
val_v = [0] * L

for r in range(N):
    for c in range(N):
        v = A[r] * B[c] % M
        val_u[r + c] += v
        val_v[r - c + ZERO] += v

sum_val_u = sum(val_u)
dist_u = [0] * L
dist_u[0] = sum(t * v for t, v in enumerate(val_u))
l = 0
for x in range(len(val_u) - 1):
    l += val_u[x]
    r = sum_val_u - l
    dist_u[x + 1] = dist_u[x] + l - r


sum_val_v = sum(val_v)
dist_v = [0] * L
dist_v[0] = sum(t * v for t, v in enumerate(val_v))
l = 0
for x in range(len(val_v) - 1):
    l += val_v[x]
    r = sum_val_v - l
    dist_v[x + 1] = dist_v[x] + l - r

ans = 0
for i in range(N):
    for j in range(N):
        v = (dist_u[i + j] + dist_v[i - j + ZERO]) // 2 + i * N + j
        ans ^= v
print(ans)
