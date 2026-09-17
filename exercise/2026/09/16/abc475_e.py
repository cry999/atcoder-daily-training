# >>> atcoder-stat >>>
# started_at  = 2026-09-15T22:42:47+09:00
# solved_at   = 2026-09-15T23:03:58+09:00
# duration_ms = 1271743
# ac          = true
# editorial   = true
# knowledge   = 3
# translation = 2
# complexity  = 3
# impl        = 1
# verify      = 3
# <<< atcoder-stat <<<
import sys

input = sys.stdin.readline


N, M, K = map(int, input().split())
T = input()
# 正解: 0 / 不正解: 1
S = [bytearray(int(s != t) for s, t in zip(input().strip(), T)) for _ in range(N)]


children = ([-1], [-1])
count = [0]


def update(bits: list[int], delta: int):
    """bits に対応するトライ木上の人数を +delta する"""
    cur = 0
    count[cur] += delta

    for bit in bits:
        if children[bit][cur] == -1:
            children[bit][cur] = len(children[bit])

            children[0].append(-1)
            children[1].append(-1)

            count.append(0)

        cur = children[bit][cur]
        count[cur] += delta

    return


def count_lte(bits: list[int]):
    """bits より小さい & 同じ人の人数を数える"""
    cur = 0
    cnt = 0

    for bit in bits:
        if bit == 1:
            c0 = children[0][cur]
            cnt += count[c0] if c0 != -1 else 0
        cur = children[bit][cur]

    return cnt + count[cur]


# トライ木の初期化
for s in S:
    update(s, 1)


Q = int(input())
ans = []
for _ in range(Q):
    i, j = map(int, input().split())
    i, j = i - 1, j - 1

    update(S[i], -1)
    S[i][j] ^= 1
    update(S[i], 1)

    if (N == M and any(b == 0 for b in S[i])) or (N != M and count_lte(S[i]) <= M):
        ans.append("Yes")
    else:
        ans.append("No")

print("\n".join(ans))
