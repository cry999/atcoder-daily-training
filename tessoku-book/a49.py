import heapq

T = int(input())
PQR = [tuple(map(int, input().split())) for _ in range(T)]


def debug(*values: object):
    # print(*values)
    pass

# # 貪欲法
# # +1, -1 それぞれの操作を行ってスコアが最大になる方を選ぶ
# X = [0] * 20
#
# for p, q, r in PQR:
#     xp, xq, xr = X[p-1], X[q-1], X[r-1]
#     score_a = (xp+1 == 0) + (xq+1 == 0) + (xr+1 == 0)
#     score_b = (xp-1 == 0) + (xq-1 == 0) + (xr-1 == 0)
#     if score_a > score_b:
#         X[p-1], X[q-1], X[r-1] = xp+1, xq+1, xr+1
#         print('A')
#     else:
#         X[p-1], X[q-1], X[r-1] = xp-1, xq-1, xr-1
#         print('B')


def operate(x: list[int], p: int, q: int, r: int, diff: int) -> list[int]:
    return [x + diff if i+1 in (p, q, r) else x for i, x in enumerate(x)]


# ビームサーチ
K = 500
dp = [[(0, '', [0]*20) for _ in range(T)] for _ in range(K)]
dp[0][0] = (17, 'A', operate([0] * 20, *PQR[0], +1))
if K > 1:
    dp[1][0] = (17, 'B', operate([0] * 20, *PQR[0], -1))

for i, (p, q, r) in enumerate(PQR[1:]):
    que = []
    debug(f'turn {i}')
    for k in range(K):
        score, op, X = dp[k][i]
        debug(score, op, X)
        xp, xq, xr = X[p-1], X[q-1], X[r-1]
        score_pqr = (xp == 0) + (xq == 0) + (xr == 0)
        diff_score_a = (xp+1 == 0) + (xq+1 == 0) + (xr+1 == 0) - score_pqr
        diff_score_b = (xp-1 == 0) + (xq-1 == 0) + (xr-1 == 0) - score_pqr
        heapq.heappush(
            que, (-(2*score+diff_score_a), op + 'A', operate(X, p, q, r, +1)))
        heapq.heappush(
            que, (-(2*score+diff_score_b), op + 'B', operate(X, p, q, r, -1)))
    k = 0
    while que and k < K:
        score, op, X = heapq.heappop(que)
        dp[k][i+1] = (-score, op, X)
        debug('pop:', dp[k][i+1][0])
        k += 1
    debug('---')

for k in range(K):
    debug(dp[k][T-1])
_, op, _ = dp[0][T-1]
for c in op:
    print(c)
