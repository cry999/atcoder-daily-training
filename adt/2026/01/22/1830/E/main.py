N = int(input())

carpet = [["."] * (3**N) for _ in range(3**N)]


def fill(i: int, j: int, level: int):
    if level == 0:
        carpet[i][j] = "#"
        return

    for x in range(3):
        for y in range(3):
            if x == 1 and y == 1:
                continue
            fill(i + x * 3 ** (level - 1), j + y * 3 ** (level - 1), level - 1)

    return


fill(0, 0, N)

for row in carpet:
    print("".join(row))
