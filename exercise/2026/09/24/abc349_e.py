# >>> atcoder-stat >>>
# started_at  = 2026-09-24T07:22:18+09:00
# solved_at   = 2026-09-24T07:30:13+09:00
# duration_ms = 475840
# ac          = true
# editorial   = false
# knowledge   = 3
# translation = 3
# complexity  = 3
# impl        = 3
# verify      = 3
# <<< atcoder-stat <<<
A = []
for _ in range(3):
    A.extend(list(map(int, input().split())))

# 考察
# 1. ある時点から、全てのパターンを確認して、自分にとっての勝ちがあるなら勝ち、そうでないなら負け

LINES = [
    (0, 1, 2),
    (3, 4, 5),
    (6, 7, 8),
    (0, 3, 6),
    (1, 4, 7),
    (2, 5, 8),
    (0, 4, 8),
    (2, 4, 6),
]
TAKAHASHI = 0
AOKI = 1


def dfs(state: list[int], turn: int):
    # 列が揃っているなら揃っている人の勝利
    for line in LINES:
        x = state[line[0]]
        if x != -1 and all(state[l] == x for l in line):
            return x

    # 全てのますが埋まっているなら得点勝負
    if all(s != -1 for s in state):
        t = sum(A[i] for i in range(9) if state[i] == TAKAHASHI)
        a = sum(A[i] for i in range(9) if state[i] == AOKI)
        return TAKAHASHI if t > a else AOKI

    for i in range(9):
        if state[i] != -1:
            continue
        state[i] = turn
        # どれか 1 手でも勝てるなら勝ち
        if dfs(state, 1 - turn) == turn:
            state[i] = -1
            return turn
        state[i] = -1

    return 1 - turn


if dfs([-1] * 9, TAKAHASHI) == TAKAHASHI:
    print("Takahashi")
else:
    print("Aoki")
