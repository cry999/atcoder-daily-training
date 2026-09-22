# >>> atcoder-stat >>>
# started_at  = 2026-09-22T17:15:35+09:00
# solved_at   = 2026-09-22T17:30:55+09:00
# duration_ms = 920887
# ac          = true
# editorial   = true
# knowledge   = 3
# translation = 1
# complexity  = 3
# impl        = 1
# verify      = 3
# <<< atcoder-stat <<<
A = []
for _ in range(3):
    A.extend(map(int, input().split()))

LINES = [
    # 横
    (0, 1, 2),
    (3, 4, 5),
    (6, 7, 8),
    # 縦
    (0, 3, 6),
    (1, 4, 7),
    (2, 5, 8),
    # 斜め
    (0, 4, 8),
    (2, 4, 6),
]

TAKAHASHI = 0
AOKI = 1


def dfs(state: list[int], turn: int):
    # 最優先として、LINE が揃っているならその人の勝利
    for line in LINES:
        if all(state[i] == 1 - turn for i in line):
            return 1 - turn

    # あきますがないなら、得点計算する
    if all(x != -1 for x in state):
        t = sum(A[i] for i in range(9) if state[i] == TAKAHASHI)
        a = sum(A[i] for i in range(9) if state[i] == AOKI)
        if t > a:
            return TAKAHASHI
        return AOKI

    # まだあきますがあるなら、それをとって自分が勝てるかを確かめる。
    for i in range(9):
        if state[i] != -1:
            continue
        state[i] = turn
        if dfs(state, 1 - turn) == turn:
            state[i] = -1
            return turn
        state[i] = -1
    # どれをとっても相手が勝つなら、相手の勝利
    return 1 - turn


if dfs([-1] * 9, TAKAHASHI) == TAKAHASHI:
    print("Takahashi")
else:
    print("Aoki")
