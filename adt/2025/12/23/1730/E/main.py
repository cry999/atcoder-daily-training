import bisect


N, K = map(int, input().split())
P = [tuple(map(int, input().split())) for _ in range(N)]

ranking = sorted([sum(p) for p in P])

for p in P:
    high_score = sum(p) + 300
    i = bisect.bisect_left(ranking, high_score)
    while i < N and ranking[i] == high_score:
        i += 1
    rank = N - i + 1
    if rank <= K:
        print("Yes")
    else:
        print("No")
