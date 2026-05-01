N = int(input())
(*A,) = map(int, input().split())

inc = [1] * N
for i in range(N - 1):
    inc[i + 1] = min(inc[i] + 1, A[i + 1])


dec = [1] * N
for i in range(N - 1, 0, -1):
    dec[i - 1] = min(dec[i] + 1, A[i - 1])


print(max(min(inc[i], dec[i]) for i in range(N)))
