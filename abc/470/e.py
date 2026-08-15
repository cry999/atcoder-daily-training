N, L = map(int, input().split())
(*A,) = map(int, input().split())

# dp[x][y][l] :=
#   残りカードが x 枚,
#   片方だけ分かっているカードが y 枚,
#   ライフが残り l の状態からのペア数の期待値
dp = [[[0] * (L + 1) for _ in range(N + 1)] for _ in range(2 * N + 1)]

for x in range(1, 2 * N + 1):
    for y in range(N + 1):
        if y > x:
            # 片方だけわかっているカードが残りカードより多くなることはない
            continue
        if x + y > 2 * N:
            # 全カード枚数を超えることはない
            continue
        if (x - y) % 2 != 0:
            continue

        z = x - y
        for l in range(1, L + 1):
            # 1 枚目が片方だけ分かっているカードの場合, 2 枚目はすでにわかっているカードをひく
            if y > 0:
                dp[x][y][l] += y / x * (1 + dp[x - 1][y - 1][l])

            if z >= 2:
                p1 = z / x
                p2 = 1 / (x - 1) * (1 + dp[x - 2][y][l])

                if y > 0 and l >= 2:
                    p2 += y / (x - 1) * (1 + dp[x - 2][y][l - 1])

                if z >= 4:
                    p2 += (z - 2) / (x - 1) * dp[x - 2][y + 2][l - 1]

                dp[x][y][l] += p1 * p2

print(dp[2 * N][0][L] * sum(A) / N)

# 検算用
#
# from itertools import permutations
# from math import perm
#
# total_score = 0
# for p in permutations(range(2 * N)):
#     seen = set()
#     deck = [A[pi % N] for pi in p]
#     score = 0
#     life = L
#     # print(f"[DEBUG] === {p=} {deck=}")
#     while deck and life:
#         # print(f"[DEBUG] {deck=} {seen=}")
#         a = deck.pop()
#         if a in seen:
#             score += a
#             seen.remove(a)
#         else:
#             b = deck.pop()
#             if a == b:
#                 score += a
#             elif b in seen:
#                 life -= 1
#                 seen.add(a)
#                 deck.append(b)
#             else:
#                 life -= 1
#                 seen.add(a)
#                 seen.add(b)
#
#     total_score += score
#
#
# print(total_score / perm(2 * N))
