A, B = map(lambda s: list(map(int, s)), input().split())


def count_forbidden(X: list[int]):
    L = len(X)
    # dp[i][c][f] :=
    # i 文字目までを決めて、
    # c: 禁止文字を利用してるか?
    # f: L < X が確定しているか?
    dp = [[[0] * 2 for _ in range(2)] for _ in range(L + 1)]
    dp[0][0][0] = 1

    for i in range(L):
        x = X[i]
        for c in range(2):  # 禁止文字を使用済みか?
            for less in range(2):  # X 以下が確定しているか?
                # X 以下が確定している場合はなんでも使っていい。
                # そうでないなら、x 以下
                stop = 9 if less else x
                for d in range(stop + 1):  # i+1 桁目の候補
                    nc = c or d == 4 or d == 9
                    nless = less or d < x
                    dp[i + 1][nc][nless] += dp[i][c][less]
    return sum(dp[L][True])


def minus_one(X: list[int]):
    L = len(X)
    carry = 1
    i = L - 1
    while carry and i >= 0:
        if X[i] == 0:
            X[i] = 9
        else:
            X[i] -= 1
            carry = 0
        i -= 1
    return X


print(count_forbidden(B) - count_forbidden(minus_one(A)))
