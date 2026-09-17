# >>> atcoder-stat >>>
# started_at  = 2026-09-17T08:20:40+09:00
# solved_at   = 2026-09-17T10:05:45+09:00
# duration_ms = 6305880
# ac          = true
# editorial   = true
# knowledge   = 2
# translation = 2
# complexity  = 2
# impl        = 1
# verify      = 2
# <<< atcoder-stat <<<
import sys

input = sys.stdin.readline


N, M, K = map(int, input().split())
T = input().strip()
S = [[int(s != t) for s, t in zip(input().strip(), T)] for _ in range(N)]

children = ([-1], [-1])
count = [0]


def update(bits: list[int], delta: int):
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
    cur, cnt = 0, 0

    for bit in bits:
        if bit == 1:
            c = children[0][cur]
            cnt += count[c] if c != -1 else 0
        cur = children[bit][cur]

    return cnt + count[cur]


# tri 木の構築
for bits in S:
    update(bits, 1)


Q = int(input())
for _ in range(Q):
    i, j = map(int, input().split())
    i, j = i - 1, j - 1

    update(S[i], -1)
    S[i][j] ^= 1
    update(S[i], 1)

    if N == M and any(b == 0 for b in S[i]):
        print("Yes")
    elif N != M and count_lte(S[i]) <= M:
        print("Yes")
    else:
        print("No")
