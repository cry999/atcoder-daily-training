N, K, X = map(int, input().split())
A = sorted(map(int, input().split()), reverse=True)

# N-K こは水の想定。
sake = 0
for i in range(N - K, N):
    sake += A[i]
    if sake >= X:
        print(i + 1)
        break
else:
    print(-1)
