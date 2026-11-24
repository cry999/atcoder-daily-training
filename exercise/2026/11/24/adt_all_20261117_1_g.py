# >>> atcoder-stat >>>
# started_at  = 2026-11-24T14:01:56+09:00
# solved_at   = 2026-11-24T14:10:44+09:00
# duration_ms = 528481
# ac          = true
# editorial   = false
# knowledge   = 3
# translation = 3
# complexity  = 3
# impl        = 3
# verify      = 3
# <<< atcoder-stat <<<
N = int(input())
A = [[list(map(int, input().split())) for _ in range(N)] for _ in range(N)]
S = [[[0] * (N + 1) for _ in range(N + 1)] for _ in range(N + 1)]

for i in range(N):
    for j in range(N):
        for k in range(N):
            S[i + 1][j + 1][k + 1] = A[i][j][k]
for i in range(N + 1):
    for j in range(N + 1):
        for k in range(N):
            S[i][j][k + 1] += S[i][j][k]
for i in range(N + 1):
    for j in range(N):
        for k in range(N + 1):
            S[i][j + 1][k] += S[i][j][k]
for i in range(N):
    for j in range(N + 1):
        for k in range(N + 1):
            S[i + 1][j][k] += S[i][j][k]
print(f"[DEBUG] {S=} {A=}")
Q = int(input())
for _ in range(Q):
    lx, rx, ly, ry, lz, rz = map(int, input().split())

    ans = S[rx][ry][rz]
    ans -= S[lx - 1][ry][rz]
    ans -= S[rx][ly - 1][rz]
    ans -= S[rx][ry][lz - 1]
    ans += S[lx - 1][ly - 1][rz]
    ans += S[lx - 1][ry][lz - 1]
    ans += S[rx][ly - 1][lz - 1]
    ans -= S[lx - 1][ly - 1][lz - 1]
    print(ans)
