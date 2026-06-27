from itertools import permutations

N, C = map(int, input().split())
D = [list(map(int, input().split())) for _ in range(C)]
G = [list(map(int, input().split())) for _ in range(N)]

hist = [[0] * C for _ in range(3)]
print(f"[DEBUG] {hist=}")
for i in range(N):
    for j in range(N):
        print(f"[DEBUG] {i=} {j=} {G[i][j]=}")
        hist[(i + j) % 3][G[i][j] - 1] += 1

ans = float("inf")
for cc in permutations(range(C), 3):
    cost = 0
    # (i+j) % 3 == d のマスを cc[d] に塗るコスト
    for d in range(3):
        for c in range(C):
            cost += hist[d][c] * D[c][cc[d]]
    ans = min(ans, cost)
print(ans)
