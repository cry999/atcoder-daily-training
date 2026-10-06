N, V = map(int, input().split())
(*W,) = map(int, input().split())

ans = 0
for i in range(N):
    for j in range(i + 1, N):
        for k in range(j + 1, N):
            w1, w2, w3 = W[i], W[j], W[k]
            if i + j + k <= V - 3:
                ans = max(ans, w1 + w2 + w3)
print(ans)
