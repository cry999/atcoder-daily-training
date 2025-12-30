import bisect


N, T = map(int, input().split())
(*A,) = map(int, input().split())

S = [0] * (N + 1)

for i in range(N):
    S[i + 1] = S[i] + A[i]

T %= S[N]
i = bisect.bisect_left(S, T)
print(i, T - S[i - 1])
