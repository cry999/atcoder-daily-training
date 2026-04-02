N, M = map(int, input().split())

this_season = [0] * M
next_season = [0] * M

for _ in range(N):
    a, b = map(lambda x: int(x) - 1, input().split())
    this_season[a] += 1
    next_season[b] += 1

for i in range(M):
    print(next_season[i] - this_season[i])
