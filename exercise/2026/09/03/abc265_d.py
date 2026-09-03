# >>> atcoder-stat >>>
# started_at  = 2026-09-03T14:31:07+09:00
# solved_at   = 2026-09-03T14:38:51+09:00
# duration_ms = 464671
# target_ms   = 900000
# ac          = true
# editorial   = false
# knowledge   = 3
# translation = 3
# complexity  = 3
# impl        = 3
# verify      = 3
# <<< atcoder-stat <<<
N, P, Q, R = map(int, input().split())
(*A,) = map(int, input().split())
S = [0] * (N + 1)
for i in range(N):
    S[i + 1] = S[i] + A[i]

y, z, w = 0, 0, 0

for x in range(N):
    y = max(y, x)
    while y <= N and S[y] - S[x] < P:
        y += 1

    if y > N or S[y] - S[x] != P:
        continue

    z = max(z, y)
    while z <= N and S[z] - S[y] < Q:
        z += 1

    if z > N or S[z] - S[y] != Q:
        continue

    w = max(w, z)
    while w <= N and S[w] - S[z] < R:
        w += 1

    if w > N or S[w] - S[z] != R:
        continue

    print("Yes")
    break
else:
    print("No")
