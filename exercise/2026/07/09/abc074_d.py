# >>> atcoder-stat >>>
# started_at  = 2026-07-09T14:42:24+09:00
# solved_at   = 2026-07-09T14:58:51+09:00
# duration_ms = 987226
# target_ms   = 900000
# ac          = true
# editorial   = true
# knowledge   = 2
# translation = 1
# complexity  = 2
# impl        = 2
# verify      = 2
# <<< atcoder-stat <<<
N = int(input())
A = [list(map(int, input().split())) for _ in range(N)]

INF = 10**18

B = [[A[i][j] for j in range(N)] for i in range(N)]
for k in range(N):
    for i in range(N):
        for j in range(N):
            B[i][j] = min(B[i][j], B[i][k] + B[k][j])

# print("\n".join(" ".join(map(str, r)) for r in dist))
ans = 0
for i in range(N):
    for j in range(i + 1, N):
        if B[i][j] < A[i][j]:
            print(-1)
            exit()
        else:
            for k in range(N):
                if k == i or k == j:
                    continue
                if B[i][k] + B[k][j] == A[i][j]:
                    # 直接辺を貼らなくても良い
                    break
            else:
                # 直接辺を貼らないと最短距離にならない。
                ans += A[i][j]


print(ans)
