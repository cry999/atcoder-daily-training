# >>> atcoder-stat >>>
# started_at  = 2026-07-19T10:05:42+09:00
# solved_at   = 2026-07-19T10:15:25+09:00
# duration_ms = 583904
# target_ms   = 900000
# ac          = true
# editorial   = true
# knowledge   = 3
# translation = 3
# complexity  = 2
# impl        = 2
# verify      = 3
# <<< atcoder-stat <<<
N = int(input())
A = [list(map(int, input().split())) for _ in range(N)]

B = [[A[i][j] for j in range(N)] for i in range(N)]

for k in range(N):
    for i in range(N):
        for j in range(N):
            B[i][j] = min(B[i][j], B[i][k] + B[k][j])

for i in range(N):
    for j in range(N):
        if B[i][j] < A[i][j]:
            print(-1)
            exit()

ans = 0
for i in range(N):
    for j in range(i + 1, N):
        for k in range(N):
            if k == i or k == j:
                continue
            if B[i][k] + B[k][j] == A[i][j]:
                # 直接辺を貼らなくても良い
                break
        else:
            # 直接辺を貼る必要があるので追加
            ans += A[i][j]
print(ans)
