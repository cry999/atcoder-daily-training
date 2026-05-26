T = int(input())

for _ in range(T):
    N, M = map(int, input().split())
    (*A,) = map(int, input().split())
    (*B,) = map(int, input().split())
    A.sort()
    B.sort(reverse=True)

    ans = 0

    i, j = 0, 0
    while i < N and j < N:
        while i < N and A[i] + B[j] < M:
            ans += A[i]
            i += 1

        if i == N:
            break
        ans += (A[i] + B[j]) % M
        i += 1
        j += 1

    while j < N:
        ans += B[j]
        j += 1

    print(ans)
