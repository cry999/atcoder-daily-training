N, M = map(int, input().split())
B = sorted(map(int, input().split()), reverse=True)
W = sorted(filter(lambda x: x > 0, map(int, input().split())), reverse=True)

M = len(W)

cum_b = [0] * (N + 1)
cum_w = [0] * (M + 1)

for i in range(N):
    cum_b[i + 1] = cum_b[i] + B[i]
for i in range(M):
    cum_w[i + 1] = cum_w[i] + W[i]

ans = max(cum_b[x] + cum_w[min(x, M)] for x in range(N + 1))

print(ans)
