N = int(input())
(*A,) = map(int, input().split())

C = [0] * (N + 1)
for i in range(N):
    C[i + 1] = C[i] + A[i]

j, k = 1, 0
ans = sum(A) + 1
for i in range(2, N - 1):
    while j + 1 < i and abs(C[i] - 2 * C[j + 1]) < abs(C[i] - 2 * C[j]):
        j += 1

    k = max(k, i)
    while k + 1 < N and abs(C[N] + C[i] - 2 * C[k + 1]) < abs(C[N] + C[i] - 2 * C[k]):
        k += 1

    print(f"[DEBUG] {i=} {j=} {k=}")
    assert j <= i < k < N

    x = max(C[N] - C[k], C[k] - C[i], C[i] - C[j], C[j])
    y = min(C[N] - C[k], C[k] - C[i], C[i] - C[j], C[j])

    print(f"[DEBUG]   {x=} {y=}")

    ans = min(ans, x - y)
print(ans)
