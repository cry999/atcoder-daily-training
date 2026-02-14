N, L, R = map(int, input().split())
(*A,) = map(int, input().split())


cum_head = [0] * (N + 1)
cum_tail = [0] * (N + 1)

for i in range(N):
    cum_head[i + 1] = min(cum_head[i] + A[i], L * (i + 1))
    cum_tail[N - i - 1] = min(cum_tail[N - i] + A[N - i - 1], R * (i + 1))

print(min(cum_head[i] + cum_tail[i] for i in range(N + 1)))
