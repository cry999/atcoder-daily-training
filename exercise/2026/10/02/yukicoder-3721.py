N, K = map(int, input().split())

# [1, N^2] の大きい方から K 個をとってくる。
# これを B = {N^2 - K + 1, N^2 - K + 2, ..., N^2} とする。
# C = {1, 2, ..., N^2 - K} とする。
# 最初 K この要素を B から並べる。すなわち A[1][1] = N^2-K+1, A[1][2] = N^2-K+2, ..., A[1][K] = N^2
# こうすると、B を並べた位置は、(1, 1) と (i, j) を対角線とする長方形の中で A[i][j] が最大になる。
# また、その後 C のそうそを並べると、それ以降は (i, j) より大きいものが並んでいるので、最大ではなく、

if K == 0:
    print(-1)
    exit()

B = []
C = []
for i in range(1, N * N + 1):
    if i > N * N - K:
        B.append(i)
    else:
        C.append(i)
C.reverse()

A = [[0] * N for _ in range(N)]
for p in range(N * N):
    i, j = divmod(p, N)
    if p < K:
        A[i][j] = B[p]
    else:
        A[i][j] = C[p - K]

for a in A:
    print(*a)
