T = int(input())

for _ in range(T):
    N = int(input())
    (*S,) = map(int, input().split())
    S = [S[0]] + sorted(S[1:-1]) + [S[-1]]
    i = 0
    ans = 0
    while i < N - 1:
        start = i
        s0 = S[i]
        while i + 1 < N and S[i + 1] <= 2 * s0:
            i += 1
        if start == i:
            break
        ans += 1
    if i == N - 1:
        print(ans + 1)
    else:
        print(-1)
