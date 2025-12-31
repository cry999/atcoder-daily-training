import sys

sys.setrecursionlimit(10**7)

N, M = map(int, input().split())
(*A,) = map(int, input().split())

m = {}
first_hand = 0
for a in A:
    m[a] = m.get(a, 0) + 1
    first_hand += a


# memo[x] := x ゲームを始めた時の最高スコア
memo = {}

if M <= N:
    # M <= N の時はループが生じ得る。
    # ループとは 0 -> 1 -> ... -> M-1 -> 0 のこと。
    # まずループがあるかどうかを確認する。
    loop_exists = True
    loop_score = 0
    for i in range(M):
        if i not in m:
            loop_exists = False
            break
        loop_score += m[i] * i
    else:
        # ループがある。
        # 先に memo にループのスコアを入れておく。
        for i in range(M):
            memo[i] = loop_score


def dfs(x: int) -> int:
    global memo, m

    if x in memo:
        return memo[x]

    if x not in m:
        return -1

    score = m[x] * x
    if ((x + 1) % M) in m:
        score += dfs((x + 1) % M)
    memo[x] = score
    return memo[x]


ans = 0
for k in m.keys():
    ans = max(ans, dfs(k))
print(first_hand - ans)
