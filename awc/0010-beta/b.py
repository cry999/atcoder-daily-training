N = int(input())
(*D,) = map(int, input().split())

prev = float("inf")
ans = 0
for i in range(N):
    if prev < D[i]:
        ans += D[i] // 2
    else:
        ans += D[i]
    prev = D[i]

print(ans)
