N, K = map(int, input().split())
*R, = map(int, input().split())


def dfs(i: int):
    if i == N-1:
        for n in range(1, R[i]+1):
            yield [n]
        return

    for n in range(1, R[i]+1):
        for nn in dfs(i+1):
            yield [n] + nn
    return


for row in dfs(0):
    if sum(row) % K == 0:
        print(*row)
