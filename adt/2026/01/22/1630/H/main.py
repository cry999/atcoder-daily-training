N = int(input())
cards = [tuple(map(int, input().split())) for _ in range(N)]

pairs = []
for i in range(N):
    ai, bi = cards[i]
    for j in range(i + 1, N):
        aj, bj = cards[j]
        if ai == aj or bi == bj:
            pairs.append((i, j))


dp = [False] * (1 << N)
for state in range(1 << N):
    if dp[state]:
        continue

    for pi, pj in pairs:
        if (state & (1 << pi)) or (state & (1 << pj)):
            # どちらかのカードがすでに使われているならスキップ
            continue

        next_state = state | (1 << pi) | (1 << pj)
        dp[next_state] = True

print(dp[-1] and "Takahashi" or "Aoki")
