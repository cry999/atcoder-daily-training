T = int(input())

for _ in range(T):
    N = int(input())
    S = input()

    left = [[0] * (N + 1) for _ in range(2)]
    right = [[0] * (N + 1) for _ in range(2)]

    num = [0] * 2
    for i in range(N):
        n = int(S[i])
        left[n][i + 1] = left[n][i]
        left[1 - n][i + 1] = 2 * num[1 - n] + num[n] + 1
        num[n] += 1

    num[0] = num[1] = 0
    for i in range(N, 0, -1):
        n = int(S[i - 1])
        right[n][i - 1] = right[n][i]
        right[1 - n][i - 1] = 2 * num[1 - n] + num[n] + 1
        num[n] += 1

    print(min(min(l + r for l, r in zip(left[i], right[i])) for i in range(2)))
