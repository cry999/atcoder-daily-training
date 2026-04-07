N, D, P = map(int, input().split())
F = sorted(map(int, input().split()), reverse=True)

ans = 0
i = 0
while i < N:
    s = sum(F[i : min(N, i + D)])
    i += D
    ans += min(s, P)
print(ans)
