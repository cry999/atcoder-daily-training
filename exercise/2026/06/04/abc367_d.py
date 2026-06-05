N, M = map(int, input().split())
(*A,) = map(int, input().split())

dist = [0] * (2 * N)
dist[0] = A[0]
for i in range(1, 2 * N):
    dist[i] = dist[i - 1] + A[i % N]
# print(dist)

hist = [0] * M
for i in range(N - 1):
    hist[dist[i] % M] += 1
# print(hist)

ans = 0
offset = 0
for i in range(N):
    ans += hist[offset]
    offset = (offset + A[i]) % M
    hist[dist[i] % M] -= 1
    hist[dist[i + N - 1] % M] += 1

print(ans)
