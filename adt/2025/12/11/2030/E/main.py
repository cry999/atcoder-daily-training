N = int(input())


def dfs(M: list[list[int]], i: int, j: int, level: int) -> int:
    if level == 0:
        M[i][j] = '#'
        return
    step = 3**(level-1)
    for ni in range(3):
        for nj in range(3):
            if ni == nj == 1:
                # 全て白くする
                pass
            else:
                # level-1 のカーペットにする。
                dfs(M, i + ni*step, j + nj*step, level-1)


def resolve(N: int) -> list[list[int]]:
    M = [['.'] * (3**N) for _ in range(3**N)]
    dfs(M, 0, 0, N)
    return M


M = resolve(N)
print('\n'.join(''.join(row) for row in M))
