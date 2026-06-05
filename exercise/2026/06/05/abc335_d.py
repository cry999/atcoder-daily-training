N = int(input())

ans = [[""] * N for _ in range(N)]
ans[N // 2][N // 2] = "T"

h, w = 0, 0
dh, dw = 0, 1
for i in range(1, N * N):
    ans[h][w] = str(i)

    if (
        h + dh < 0
        or N <= h + dh
        or w + dw < 0
        or N <= w + dw
        or ans[h + dh][w + dw] != ""
    ):
        dh, dw = dw, -dh

    h += dh
    w += dw

for row in ans:
    print(*row)
