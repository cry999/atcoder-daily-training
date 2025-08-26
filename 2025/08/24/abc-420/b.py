N, M = map(int, input().split())

S = [input() for _ in range(N)]
scores = [0] * N

for i in range(M):
    x = len(list(filter(lambda s: s[i] == '0', S)))
    y = N - x

    if x == 0 or y == 0:
        for j in range(N):
            scores[j] += 1
    elif x < y:
        for j in range(N):
            scores[j] += S[j][i] == '0'
    else:
        for j in range(N):
            scores[j] += S[j][i] == '1'

max_score = max(scores)

# print(scores)

print(' '.join(
    map(lambda x: str(x+1), filter(lambda i: scores[i] == max_score, range(N)))))
