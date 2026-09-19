# >>> atcoder-stat >>>
# started_at  = 2026-09-18T19:38:12+09:00
# solved_at   = 2026-09-18T20:19:32+09:00
# duration_ms = 2480818
# target_ms   = 900000
# ac          = true
# editorial   = true
# knowledge   = 3
# translation = 1
# complexity  = 3
# impl        = 1
# verify      = 3
# <<< atcoder-stat <<<
from itertools import permutations

N = int(input())
R = input()
C = input()

LETTERS = "ABC"

# candidates[i] = i 行目の列の候補
candidates: list[list[tuple[int, int, int]]] = [[] for _ in range(N)]

# positions: [A の列番号, B の列番号, C の列番号]
for positions in permutations(range(N), 3):
    # 列番号が最小の文字
    first = LETTERS[min(range(3), key=lambda k: positions[k])]

    for i in range(N):
        if first == R[i]:
            candidates[i].append(positions)

# used[j] = j 列目に文字 (ABC) が使われたか
used = [set() for _ in range(N)]

# 採用した各行の文字列
ans = []


def dfs(i: int):
    """i 行目を探索"""
    if i == N:
        return all(len(s) == 3 for s in used)

    for positions in candidates[i]:
        ok = True

        for c, j in zip(LETTERS, positions):
            if c in used[j]:
                # すでに c は j 列目で使われている
                ok = False
                break

            if not used[j] and c != C[j]:
                # j 列目の最初の文字だが、j 列目の先頭におくべき文字ではない
                ok = False
                break

        if not ok:
            continue

        row = ["."] * N
        for c, j in zip(LETTERS, positions):
            row[j] = c
            used[j].add(c)

        ans.append("".join(row))

        if dfs(i + 1):
            return True

        ans.pop()
        for c, j in zip(LETTERS, positions):
            used[j].remove(c)

    return False


if dfs(0):
    print("Yes")
    print("\n".join(ans))
else:
    print("No")
