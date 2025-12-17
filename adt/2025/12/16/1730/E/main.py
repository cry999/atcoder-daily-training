N, M = map(int, input().split())
S = [input() for _ in range(N)]

ans = N
for bits in range(1 << N):
    n = 0
    bought = [False]*M
    for i in range(N):
        if not bits & (1 << i):
            continue
        n += 1
        for j in range(M):
            if S[i][j] == 'o':
                bought[j] = True
    if all(bought):
        ans = min(ans, n)

print(ans)
