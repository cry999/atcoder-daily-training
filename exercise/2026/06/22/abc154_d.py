N, K = map(int, input().split())
(*p,) = map(int, input().split())
e = [(p[i] + 1) / 2 for i in range(N)]

s = sum(e[:K])
ans = s
for i in range(N - K):
    s -= e[i]
    s += e[i + K]
    ans = max(ans, s)
print(ans)
