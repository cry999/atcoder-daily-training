from bisect import bisect_left as bl


N, L, R = map(int, input().split())
(*P,) = map(int, input().split())

scores = sorted([(P[i], i + 1) for i in range(N)])

i = bl(scores, (R, 0))
if i == N or scores[i][0] > R:
    i -= 1

if i < 0 or not (i < N and L <= scores[i][0] <= R):
    print(-1)
else:
    while i - 1 >= 0 and scores[i - 1][0] == scores[i][0]:
        i -= 1
    print(scores[i][1])
