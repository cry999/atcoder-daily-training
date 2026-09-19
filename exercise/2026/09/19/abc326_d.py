# >>> atcoder-stat >>>
# started_at  = 2026-09-19T09:59:53+09:00
# solved_at   = 2026-09-19T10:15:41+09:00
# duration_ms = 948597
# target_ms   = 900000
# ac          = true
# editorial   = false
# knowledge   = 3
# translation = 3
# complexity  = 3
# impl        = 3
# verify      = 3
# <<< atcoder-stat <<<
from itertools import permutations

N = int(input())
R = input()
C = input()

LETTERS = "ABC"

# 各行の ABC の位置の候補を作る
candidates: list[list[tuple[int, ...]]] = [[] for _ in range(N)]

for positions in permutations(range(N), 3):
    # positions[0, 1, 2] は 0 = A, 1 = B, 2 = C の位置を表す

    # 一番左に来る文字を見つける。
    left = min(range(3), key=lambda k: positions[k])
    for r in range(N):
        # 先頭の文字が一致する行で使う候補に追加する。
        if LETTERS[left] == R[r]:
            candidates[r].append(positions)

# あとは全列挙

# used[i] := i 列目で使われた文字の集合
used = [set() for _ in range(N)]

# ans[i] := i 行目に使う文字の位置の候補
ans = []


def dfs(r: int):
    if r == N:
        # 全ての列で ABC が 1 文字ずつ使われているなら成功
        return all(len(used[i]) == 3 for i in range(N))

    for positions in candidates[r]:
        # 使えるかどうかを確認する
        can_use = True
        for c, j in zip(LETTERS, positions):
            # すでに使われている文字が列にある場合は使えない
            if c in used[j]:
                can_use = False
                break

            # 列の先頭の文字になるなら C[j] と一致していないと使えない
            if not used[j] and C[j] != c:
                can_use = False
                break

        if not can_use:
            continue

        row = ["."] * N
        for c, j in zip(LETTERS, positions):
            row[j] = c
            used[j].add(c)

        ans.append("".join(row))

        if dfs(r + 1):
            return True

        # 後始末
        ans.pop()
        for c, j in zip(LETTERS, positions):
            used[j].remove(c)

    return False


if dfs(0):
    print("Yes")
    print("\n".join(ans))
else:
    print("No")
