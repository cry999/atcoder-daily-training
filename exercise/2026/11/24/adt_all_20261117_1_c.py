# >>> atcoder-stat >>>
# started_at  = 2026-11-24T13:06:43+09:00
# solved_at   = 2026-11-24T13:09:25+09:00
# duration_ms = 162571
# ac          = true
# editorial   = false
# knowledge   = 3
# translation = 3
# complexity  = 3
# impl        = 3
# verify      = 3
# <<< atcoder-stat <<<
H, W = map(int, input().split())
A = [input() for _ in range(H)]
B = [input() for _ in range(H)]

for st in range(H * W):
    s, t = divmod(st, W)
    for ij in range(H * W):
        i, j = divmod(ij, W)
        k, l = (i + s) % H, (j + t) % W
        if A[i][j] != B[k][l]:
            break
    else:
        print("Yes")
        break
else:
    print("No")
