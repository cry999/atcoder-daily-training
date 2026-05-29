T = int(input())

for _ in range(T):
    N = int(input())
    S = input()

    # left[i][0|1] := S[:i] を 0|1 にするのに必要な操作回数
    left = [[0] * 2 for _ in range(N + 1)]

    for i in range(N):
        left[i + 1][0] = left[i][0] + (S[i] == "1")
        left[i + 1][1] = left[i][1] + (S[i] == "0")

    # print(S)
    # print("[0]", *[left[i][0] for i in range(N + 1)])
    # print("[1]", *[left[i][1] for i in range(N + 1)])
    max_prev = left[0][1] - left[0][0]
    ans = N
    for l in range(N + 1):
        cur = left[l][1] - left[l][0]
        max_prev = max(max_prev, cur)
        ans = min(ans, cur - max_prev)
    print(left[N][0] + ans)
