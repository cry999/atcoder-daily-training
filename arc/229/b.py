INF = 10**18

T = int(input())
for _ in range(T):
    N = int(input())
    (*A,) = map(int, input().split())

    ans = int(A[-1] > 0)
    for i in range(N - 1):
        d = A[i] - 2 * A[i + 1]
        if d < 0:
            ans = -1
            break
        ans = max(ans, d)
    print(ans)
