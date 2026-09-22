# >>> atcoder-stat >>>
# started_at  = 2026-09-21T10:39:20+09:00
# solved_at   = 2026-09-21T10:44:20+09:00
# duration_ms = 300655
# ac          = true
# editorial   = false
# knowledge   = 3
# translation = 3
# complexity  = 3
# impl        = 3
# verify      = 3
# <<< atcoder-stat <<<
N, X, Y = map(int, input().split())
(*A,) = map(int, input().split())

# 区間の右側を固定しながら尺取法を実施するとした時、固定した右端に対して、
# last_inv より右で、min(last_min, last_max) より左に含まれる x が左端候補となる。
last_min, last_max, last_inv = -1, -1, -1
ans = 0

for right in range(N):
    if A[right] < Y or X < A[right]:
        last_inv = right
    if A[right] == X:
        last_max = right
    if A[right] == Y:
        last_min = right

    ans += max(0, min(last_min, last_max) - last_inv)
print(ans)
