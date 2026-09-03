# >>> atcoder-stat >>>
# started_at  = 2026-09-03T16:08:11+09:00
# solved_at   = 2026-09-03T16:33:31+09:00
# duration_ms = 1520916
# ac          = true
# editorial   = false
# knowledge   = 3
# translation = 3
# complexity  = 3
# impl        = 2
# verify      = 3
# <<< atcoder-stat <<<
N, D = map(int, input().split())

x = [0] * N
y = [0] * N
for i in range(N):
    x[i], y[i] = map(int, input().split())

x.sort()
y.sort()

sx = [0] * (N + 1)
sy = [0] * (N + 1)
for i in range(N):
    sx[i + 1] = sx[i] + x[i]
    sy[i + 1] = sy[i] + y[i]

dist_x = [0] * (D + 1)
dist_y = [0] * (D + 1)

M = 10**6
ix, iy = 0, 0
for z in range(-2 * M, 2 * M + 1):
    while ix < N and x[ix] < z:
        ix += 1

    dx = sx[N] - 2 * sx[ix] - (N - 2 * ix) * z
    assert dx >= 0
    if dx <= D:
        dist_x[dx] += 1

    while iy < N and y[iy] < z:
        iy += 1

    dy = sy[N] - 2 * sy[iy] - (N - 2 * iy) * z
    assert dy >= 0
    if dy <= D:
        dist_y[dy] += 1


for d in range(D):
    dist_y[d + 1] += dist_y[d]

ans = 0
for d in range(D + 1):
    ans += dist_x[d] * dist_y[D - d]
print(f"[DEBUG] {dist_x=}, {dist_y=}")
print(ans)
