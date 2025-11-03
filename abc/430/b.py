N, M = map(int, input().split())
S = [input() for _ in range(N)]

m = {}

for i in range(N-M+1):
    for j in range(N-M+1):
        s = ''
        for di in range(M):
            for dj in range(M):
                s += S[i+di][j+dj]
        m[s] = 1

print(sum(m.values()))
