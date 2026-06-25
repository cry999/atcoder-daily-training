import sys

input = sys.stdin.readline


N, M, Q = map(int, input().split())
cum2d = [[0] * (N + 1) for _ in range(N + 1)]
for _ in range(M):
    l, r = map(int, input().split())
    cum2d[l][r] += 1

for i in range(N + 1):
    for j in range(N):
        cum2d[i][j + 1] += cum2d[i][j]

for i in range(N):
    for j in range(N + 1):
        cum2d[i + 1][j] += cum2d[i][j]

for _ in range(Q):
    p, q = map(int, input().split())

    ans = cum2d[N][q] - cum2d[p - 1][q]
    print(ans)
