N, M = map(int, input().split())
*A, = map(int, input().split())

s = sum((i+1)*A[i] for i in range(M))
max_s = s

cum = [0] * (N+1)
for i in range(N):
    cum[i+1] = cum[i] + A[i]

for i in range(M, N):
    # cum[i]-cum[i-M] = A[i-1] + A[i-2] + ... A[i-M]
    s = s - (cum[i]-cum[i-M]) + A[i]*M
    max_s = max(max_s, s)

print(max_s)
