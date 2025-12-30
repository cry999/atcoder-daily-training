N, M = map(int, input().split())
*B, = sorted(map(int, input().split()), reverse=True)
*W, = sorted(map(int, input().split()), reverse=True)

ans = 0
for i in range(N):
    if i < M:
        if B[i]+W[i] >= B[i] and B[i]+W[i] > 0:
            ans += B[i]+W[i]
        elif B[i] >= B[i]+W[i] and B[i] > 0:
            ans += B[i]
    else:
        if B[i] > 0:
            ans += B[i]
print(ans)
