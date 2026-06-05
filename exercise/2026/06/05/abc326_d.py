from itertools import permutations
from collections import Counter

N = int(input())
R = input()
C = input()

STRING = "ABC" + ("." * (N - 3))


def head_row_is_valid(row: str):
    for i in range(N):
        if R[i] == row[i] or row[i] == ".":
            continue
        return False
    return True


def head_col_is_valid(col: str):
    for i in range(N):
        if C[i] == col[i] or col[i] == ".":
            continue
        return False
    return True


def col(puzzle: list[str], j: int):
    return "".join(puzzle[i][j] for i in range(N))


def generate_puzzle(n: int = 0, product: list[str] = None):
    if n == N:
        yield product[:]
    else:
        if product is None:
            product = []

        for perm in permutations(STRING):
            if n == 0 and not head_row_is_valid(perm):
                continue
            if perm[0] != C[n] and perm[0] != ".":
                continue

            copy = product.copy()
            copy.append("".join(perm))
            yield from generate_puzzle(n + 1, copy)


for puzzle in generate_puzzle():
    # print(puzzle)
    # 先頭行が R に反していないことをチェック
    if not head_row_is_valid(puzzle[0]):
        continue

    # 先頭列が C に反していないことをチェック

    if not head_col_is_valid(col(puzzle, 0)):
        continue

    # 各行に A, B, C が 1 つずつ含まれていることは生成方法から確定している。
    # 各列について確認する。
    row_is_satisfied = True

    for j in range(N):
        c = Counter(puzzle[i][j] for i in range(N))
        if c.get("A", 0) == c.get("B", 0) == c.get("C", 0) == 1:
            continue
        row_is_satisfied = False
        break

    if not row_is_satisfied:
        continue

    for row in puzzle:
        print(row)
    break
