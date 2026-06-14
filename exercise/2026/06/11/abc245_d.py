N, M = map(int, input().split())
(*A,) = map(int, input().split())
(*C,) = map(int, input().split())
B = [0] * (M + 1)

for m in range(M, -1, -1):
    s = 0
    for n in range(N, -1, -1):
        k = m + (N - n)
        if k > M:
            continue
        s += A[n] * B[k]

    B[m] = (C[N + m] - s) // A[N]

print(*B)
