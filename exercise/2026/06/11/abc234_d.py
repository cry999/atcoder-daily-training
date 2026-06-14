N, K = map(int, input().split())
(*P,) = map(int, input().split())

cur = N - K + 1
ans = [0] * (N - K + 1)
ans[N - K] = cur
usable = [True] * (N + 1)
for i in range(N - 1, K - 1, -1):
    usable[P[i]] = False
    if cur <= P[i]:
        cur -= 1
        while not usable[cur]:
            cur -= 1
    ans[i - K] = cur

print("\n".join(map(str, ans)))
