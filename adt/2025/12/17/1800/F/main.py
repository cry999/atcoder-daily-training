N = int(input())
S = [input() for _ in range(N)]


def ok(i: int, j: int, di: int, dj: int) -> bool:
    return 0 <= i+5*di < N and 0 <= j+5*dj < N and sum(
        S[i+k*di][j+k*dj] == '.' for k in range(6)
    ) <= 2


for i in range(N):
    for j in range(N):
        for di, dj in [(0, 1), (1, 0), (1, 1), (1, -1)]:
            if ok(i, j, di, dj):
                print('Yes')
                exit()
print('No')
