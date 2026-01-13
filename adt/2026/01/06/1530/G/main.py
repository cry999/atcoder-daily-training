from collections import defaultdict


N, T = map(int, input().split())
scores = [0] * (N + 1)
score_hist = defaultdict(int)
score_hist[0] = N

ans = 1  # 最初は全て 0 で一種類
for _ in range(T):
    a, b = map(int, input().split())
    score_hist[scores[a]] -= 1
    if score_hist[scores[a]] == 0:
        # 一つスコアの種類が減った。
        ans -= 1

    scores[a] += b
    if score_hist[scores[a]] == 0:
        # まだ出現していないスコアの種類が増える
        ans += 1
    score_hist[scores[a]] += 1

    print(ans)
